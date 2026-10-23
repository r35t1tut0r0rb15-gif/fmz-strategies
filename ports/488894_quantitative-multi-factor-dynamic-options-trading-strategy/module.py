"""Hourly bars: the close crossing over the upper Bollinger band (20, 2) with RSI 14 over 60, volume over 1.5 x its 10-bar average, the close above the VWMA 20 and ATR 14 over half its 20-bar average goes long; the mirror at the lower band goes short; a close 2 ATR beyond the fill (target), 1.5 ATR against it (stop) or the 3rd bar after the fill closes the trade at the next open; reversing.
Port of FMZ strategy #488894 "Quantitative Multi Factor Dynamic Options Trading Strategy" (Vinayz Options Stratergy).

FMZ source id: 488894

Source
    https://www.fmz.com/strategy/488894 (PineScript v6, FMZ last modified 2025-03-31 16:38:05).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 144-231), BB 20 x 2; RSI 14 (60 / 40); volume SMA 10 x 1.5; VWMA 20 ("VWAP"); ATR 14 filter; target 2 ATR, stop 1.5 ATR from position_avg_price (current ATR); hold 3 bars; 2 % of equity
    longCE = crossover(close, upperBB) and rsi > 60 and volSpike and close > vwma20 and atrFilter -> entry CE Entry;  longPE mirrored -> entry PE Entry
    long: close >= avg + 2 atr -> close;  close <= avg - 1.5 atr -> close;  bar_index - entry_bar_index >= 3 -> close  (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are close tests at the bar's close against the fill price and the CURRENT ATR, with
      market closes, so they fill at the next open (exact in the signals). The entry bar index is the
      fill bar, so the time close is sent on the 3rd bar after it. An opposite entry reverses. The
      "VWAP" is ta.vwma(close, 20). The title names options; the rules are generic. REVERSAL INTENDED.
      2 % of equity is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked ATR target / stop and a 3-bar time exit in the signals.
    2 generic: PASS, Bollinger breakouts on volume with RSI, VWMA and volatility filters.
    3 crypto-exchange-only: no (exchange pair in the header only (Bank Nifty named in the alerts)).
    4 signals only: 2 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.5 x its SMA 10 and as the VWMA weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488894_bollinger_breakout_volume_vwma_atr_close_exits_3bar_1h_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hold": [3, 6],
    "tp_atr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"hold": 3, "tp_atr": 2.0, "sl_atr": 1.5}


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
    pc = c.shift(1)
    atr = _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), 14)
    basis, dev = c.rolling(20).mean(), 2 * c.rolling(20).std(ddof=0)
    up_b, lo_b = basis + dev, basis - dev
    r = _rsi(c, 14)
    vw = (c * v).rolling(20).mean() / v.rolling(20).mean()
    ok = (v > v.rolling(10).mean() * 1.5) & (atr > atr.rolling(20).mean() * 0.5)
    buy = ((c > up_b) & (c.shift(1) <= up_b.shift(1)) & (r > 60) & ok & (c > vw)).to_numpy()
    sell = ((c < lo_b) & (c.shift(1) >= lo_b.shift(1)) & (r < 40) & ok & (c < vw)).to_numpy()
    on, cn, an = o.to_numpy(dtype=float), c.to_numpy(dtype=float), atr.to_numpy(dtype=float)
    tpk, slk, hold = float(p["tp_atr"]), float(p["sl_atr"]), int(p["hold"])
    m = len(cn)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    tgt, held_prev, fp, fbar = 0, 0, np.nan, -1
    for i in range(m):
        held = tgt                          # the position after this bar's open
        if held != 0 and held != held_prev:
            fp, fbar = on[i], i             # a new trade filled at this open
        new = held
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if new == held and held != 0:
            a = an[i]
            if held == 1 and (cn[i] >= fp + tpk * a or cn[i] <= fp - slk * a or i - fbar >= hold):
                new = 0
            elif held == -1 and (cn[i] <= fp - tpk * a or cn[i] >= fp + slk * a or i - fbar >= hold):
                new = 0
        if new != held and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif held == 1:
                lx[i] = True
            else:
                sx[i] = True
            tgt = new
        held_prev = held
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
