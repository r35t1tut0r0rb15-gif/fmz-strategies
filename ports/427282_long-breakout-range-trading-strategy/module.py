"""Breakout range, long only: a high above the highest high of the previous 4 bars goes long (from
flat); the first bar without such a breakout closes the long.
Port of FMZ strategy #427282 "Long Breakout Range Trading Strategy".

FMZ source id: 427282

Source
    https://www.fmz.com/strategy/427282 (PineScript v2, FMZ last modified 2023-09-19 17:19:55).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 176-188), look back 4, reverse off
    pos = high > highest(high, 4)[1] ? 1 : 0
    pos == 1 and flat -> entry long; pos == 0 and long -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * highest(high, 4)[1] covers the 4 bars before the current one (the current bar excluded).
    * "Trade reverse" is off: long only. One signal per bar.
    * FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bar counts only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427282_breakout_range_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "look_back": [4, 8, 16],
}
DEFAULT_PARAMS = {"look_back": 4}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    n = int({**DEFAULT_PARAMS, **params}["look_back"])
    h = bars_df["high"]
    brk = (h > h.rolling(n).max().shift(1)).to_numpy()
    m = len(brk)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and brk[i]:
            le[i], pos = True, 1
        elif pos == 1 and not brk[i]:
            lx[i], pos = True, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
