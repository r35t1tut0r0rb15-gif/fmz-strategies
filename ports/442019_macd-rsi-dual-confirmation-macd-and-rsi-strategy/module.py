"""Hourly bars: the first up bar after a down bar (not two in a row) together with the MACD 5 / 13 / 5 crossing over its signal, RSI 14 not above 70 and volume above its 20-bar average goes long; the mirror goes short; a long closes at the next up bar after a down bar, a short at the next down bar after an up bar; reversing.
Port of FMZ strategy #442019 "基于MACD和RSI的双确认入场策略Dual-Confirmation-MACD-and-RSI-Strategy" (Al-Sat Sinyali ve Teyidi (MACD + RSI + volume)).

FMZ source id: 442019

Source
    https://www.fmz.com/strategy/442019 (PineScript v5, FMZ last modified 2024-02-18 16:24:06).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 102-129), MACD 5 / 13 / 5; RSI 14, 70 / 30; volume SMA 20
    shouldBuy = crossover(close, open) and not crossover(close[1], open[1]) and crossover(macd, signal) and not rsi > 70 and volume > sma(volume, 20) -> entry Buy;  shouldSell mirror -> entry Sell
    close Buy when crossover(close, open);  close Sell when crossunder(close, open)

Interpretation choices (Pine rules in SURVEY_README.md)
    * crossover(close, open) is an up bar after a bar that was not up. The close calls fire on the
      same bar kind that opens the trade; a close acts only on a position the bar's entries leave
      unchanged, so a long opened on such a bar is held until the next one (weird case). REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle-colour flips confirmed by MACD crossings, RSI and volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442019_candle_flip_macd5_13_cross_rsi_volume_1h_reversal"
FAMILY = "macd_variant"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 12],
    "slow": [13, 26],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 13, "signal": 5}


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
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    rsi = _rsi(c, 14)
    vol_ok = v > v.rolling(20).mean()
    flip_up = (c > o) & (c.shift(1) <= o.shift(1))
    flip_dn = (c < o) & (c.shift(1) >= o.shift(1))
    m_up = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & ~(rsi > 70)
    m_dn = (macd < sig) & (macd.shift(1) >= sig.shift(1)) & ~(rsi < 30)
    buy = (flip_up & ~flip_up.shift(1, fill_value=False) & m_up & vol_ok).to_numpy()
    sell = (flip_dn & ~flip_dn.shift(1, fill_value=False) & m_dn & vol_ok).to_numpy()
    fu, fd = flip_up.to_numpy(), flip_dn.to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and fu[i]:
                new = 0
            elif pos == -1 and fd[i]:
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
