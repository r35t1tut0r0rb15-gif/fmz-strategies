"""A "dynamic" EMA 5 (of the low above the SMA 13 trend, of the high below it) crossing the SMA 10 in an ordered trend, hourly bars: crossing over with fast >= slow >= trend goes long, crossing under with fast <= slow <= trend goes short; the opposite fast / slow crossing closes; reversing.
Port of FMZ strategy #430371 "Moving Average Crossover Strategy" (Moving Average Crossover).

FMZ source id: 430371

Source
    https://www.fmz.com/strategy/430371 (PineScript v5, FMZ last modified 2023-10-27 16:19:00).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 199-356), fast EMA 5 (dynamic source on), slow SMA 10, trend SMA 13; entries Fast-Slow in trend; exits Fast-Slow; filters, SL and TP off
    crosslong = crossover(Fast, Slow) and uptrend -> entry long;  crossshort = crossunder(Fast, Slow) and downtrend -> entry short
    crossunder(Fast, Slow) -> close long;  crossover(Fast, Slow) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The dynamic EMA takes the low when the close is above the trend SMA and the high otherwise, as written.
      The volume, ATR and RSI filters and the stop / target are switched off, so volume does not reach the
      orders: ported as not using volume (check 8). The closes act only on a position the bar's entries
      leave unchanged. REVERSAL INTENDED. The 10 % of equity size is sizing. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, dynamic EMA / SMA crossings in an ordered trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity, capital 100000 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430371_dynamic_ema5_sma10_trend13_cross_reversal"
FAMILY = "ma_crossover"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema1": [5, 9],
    "sma1": [10, 20],
}
DEFAULT_PARAMS = {"ema1": 5, "sma1": 10, "sma2": 13}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    trend = c.rolling(int(p["sma2"])).mean()
    fast = lo.where(c > trend, h).ewm(span=int(p["ema1"]), adjust=False).mean()
    slow = c.rolling(int(p["sma1"])).mean()
    up = (fast > slow) & (fast.shift(1) <= slow.shift(1))
    dn = (fast < slow) & (fast.shift(1) >= slow.shift(1))
    uptrend = (fast >= slow) & (slow >= trend)
    downtrend = (fast <= slow) & (slow <= trend)
    lc, sc = (up & uptrend).to_numpy(), (dn & downtrend).to_numpy()
    lxc, sxc = dn.to_numpy(), up.to_numpy()
    m = len(lc)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        old = pos
        if lc[i]:
            pos = 1
        if sc[i]:
            pos = -1
        if lxc[i] and old == 1 and pos == 1:
            pos = 0
        if sxc[i] and old == -1 and pos == -1:
            pos = 0
        if pos == 1 and old != 1:
            le[i] = True
        elif pos == -1 and old != -1:
            se[i] = True
        elif pos == 0 and old == 1:
            lx[i] = True
        elif pos == 0 and old == -1:
            sx[i] = True
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
