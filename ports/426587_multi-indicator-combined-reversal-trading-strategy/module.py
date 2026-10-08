"""Combo 123 Reversal & CMO disparity (HPotter): long when the 123-reversal state and the EMA
disparity state are both +1, short when both are -1, flat otherwise.
Port of FMZ strategy #426587 "Multi indicator Combined Reversal Trading Strategy".

Source
    https://www.fmz.com/strategy/426587 (PineScript v2/v3 syntax, FMZ last modified 2023-09-13 15:04:40).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 95-136), 14 / 1 / 3 / 50, EMA 50 / 25 / 10
    pos123 as HPotter's 123 reversal (stoch 14, smoothing 1 / 3, level 50)
    res_n = 100 (close - ema(close, n)) / close
    posCMOD = res10 > res50 ? -1 : res10 < res25 ? 1 : previous
    both +1 -> entry long; both -1 -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Trade reverse" off (source default). strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426587_combo_123_reversal_cmo_disparity"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21],
    "len_first": [50],
    "len_second": [25, 20],
    "len_third": [10, 5],
}
DEFAULT_PARAMS = {"length": 14, "k_smooth": 1, "d_length": 3, "level": 50,
                  "len_first": 50, "len_second": 25, "len_third": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(target, index):
    """Signals from the position each bar's orders leave (1 / 0 / -1): a change to +-1 is an
    entry (reversing an opposite position), a change to 0 an exit of the side held."""
    m = len(target)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    prev = 0
    for i in range(m):
        n = target[i]
        if n != prev:
            if n == 1:
                le[i] = True
            elif n == -1:
                se[i] = True
            elif prev == 1:
                lx[i] = True
            else:
                sx[i] = True
        prev = n
    return tuple(pd.Series(x, index=index) for x in (le, lx, se, sx))


def _state(up, dn):
    out = np.zeros(len(up))
    prev = 0.0
    for i in range(len(up)):
        prev = 1.0 if up[i] else (-1.0 if dn[i] else prev)
        out[i] = prev
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    lo, hi = l.rolling(n).min(), h.rolling(n).max()
    fast = (100 * (c - lo) / (hi - lo)).rolling(int(p["k_smooth"])).mean()
    slow = fast.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    a = _state(((c2 < c1) & (c > c1) & (fast < slow) & (fast > p["level"])).to_numpy(),
               ((c2 > c1) & (c < c1) & (fast > slow) & (fast < p["level"])).to_numpy())
    res = lambda k: 100 * (c - c.ewm(span=int(k), adjust=False).mean()) / c
    r1, r2, r3 = res(p["len_first"]), res(p["len_second"]), res(p["len_third"])
    # the -1 test comes first in the source
    b = _state(((r3 < r2) & ~(r3 > r1)).to_numpy(), (r3 > r1).to_numpy())
    target = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0))
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
