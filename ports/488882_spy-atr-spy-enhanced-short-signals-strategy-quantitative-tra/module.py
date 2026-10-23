"""Hourly bars, short only: a close within 1 % of the 20-bar high (or crossing under it) with RSI 20 under 45, MACD under its signal and volume over 1.5 x its 20-bar average goes short; a 1.5 ATR target and 1 ATR stop from position_avg_price are armed only when a signal repeats during the trade, followed in the signals.
Port of FMZ strategy #488882 "SPY增强型空头信号策略-基于动态ATR目标优化的量化交易系统-SPY-Enhanced-Short-Signals-Strategy-Quantitative-Trading-System-with-Dynamic-ATR-Target-Optimization" (SPY Enhanced Short Signals - Fixed).

FMZ source id: 488882

Source
    https://www.fmz.com/strategy/488882 (PineScript v6, FMZ last modified 2025-03-31 15:40:06).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 164-214), 20-bar high / low; RSI 20 < 45; MACD 12 / 26 / 9; volume SMA 20 x 1.5; ATR 14 x 1.5 / 1.0; 10 % of equity
    enterShort = (close >= highest(high, 20) x 0.99 or crossunder(close, highest(high, 20))) and rsi(20) < 45 and macd < signal and volume > 1.5 x sma(volume, 20) -> entry Short, exit(limit = position_avg_price - 1.5 atr, stop = position_avg_price + 1.0 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit takes position_avg_price at the signal bar: na when the signal opens the trade from flat,
      so no exit exists; only a repeated signal during the trade arms it, from the trade's fill and that
      bar's ATR. The house engine cannot arm a bracket later, so the signals follow it: a bar whose high
      reaches the armed stop or whose low reaches the target closes the trade at the next open (mark
      trailing_stop_pending). The title names SPY; the header is ETH_USDT. Opposite entries cannot occur
      (short only). 10 % of equity is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; position-price bracket followed in the signals.
    2 generic: PASS, failed tests of the 20-bar high on volume with bearish momentum.
    3 crypto-exchange-only: no (exchange pair in the header only (SPY named in the title)).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.5 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Opposite entries cannot occur (short only).

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488882_resistance_short_rsi_macd_volume_late_atr_bracket_1h_short_only"
FAMILY = "resistance_fade"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tp_atr": [1.5, 2.5],
    "sl_atr": [1.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "rsi_max": 45.0, "vol_mult": 1.5, "tp_atr": 1.5, "sl_atr": 1.0}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    n = int(p["length"])
    res = h.rolling(n).max()
    near = (c >= res * 0.99) | ((c < res) & (c.shift(1) >= res.shift(1)))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    sell = (near & (_rsi(c, 20) < float(p["rsi_max"])) & (macd < sig)
            & (v > v.rolling(20).mean() * float(p["vol_mult"]))).to_numpy()
    pc = c.shift(1)
    atr = _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), 14).to_numpy()
    on, hn, ln = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    tpk, slk = float(p["tp_atr"]), float(p["sl_atr"])
    m = len(on)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    vpos, pine, fp, pend, armed = 0, 0, np.nan, False, None
    for i in range(m):
        held = pine
        if pend:
            fp, pend = on[i], False
        if held == -1 and armed is not None and (hn[i] >= armed[0] or ln[i] <= armed[1]):
            held, armed, fp = 0, None, np.nan
        new = held
        if sell[i]:
            if held == -1:
                armed = (fp + slk * atr[i], fp - tpk * atr[i])   # position_avg_price is known only now
            else:
                new, pend, armed = -1, True, None
        pine = new
        if new != vpos and i + 1 < m:
            if new == -1:
                se[i] = True
            else:
                sx[i] = True
            vpos = new
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return false, false.copy(), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
