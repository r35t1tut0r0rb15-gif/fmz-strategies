"""Donchian breakout, long only: the close crossing above the previous bar's 20-bar highest high
goes long; crossing under the previous bar's 20-bar lowest low closes it.
Port of FMZ strategy #426895 "Breakout Tracking Strategy".

Source
    https://www.fmz.com/strategy/426895 (PineScript v2/v3 syntax, FMZ last modified 2023-09-15 12:36:43).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 144-166), length 20, exit option 1
    crossover(close, highest(20)[1]) -> entry long;  crossunder(close, lowest(20)[1]) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Exit option 1 (lower band, source default); option 2 (basis) is the grid's other value.
    * Same bar: from flat the entry stands; while long the close goes flat. Long only.
    * FREQ = "5min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426895_donchian_breakout_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 55],
    "exit_option": [1, 2],
}
DEFAULT_PARAMS = {"length": 20, "exit_option": 1}


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


def _long_only(entry, out, index):
    """Pine order for a long-only script: an entry from flat stands (a close finds no position at
    the close); while long the entry is refused and the close goes flat."""
    target = np.zeros(len(entry), dtype=int)
    pos = 0
    for i in range(len(entry)):
        if pos == 0 and entry[i]:
            pos = 1
        elif pos == 1 and out[i]:
            pos = 0
        target[i] = pos
    return _emit(target, index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    c = bars_df["close"]
    upper, lower = bars_df["high"].rolling(n).max(), bars_df["low"].rolling(n).min()
    ref = lower if int(p["exit_option"]) == 1 else (upper + lower) / 2
    u1, r1 = upper.shift(1), ref.shift(1)
    entry = ((c > u1) & (c.shift(1) <= u1.shift(1))).to_numpy()
    out = ((c < r1) & (c.shift(1) >= r1.shift(1))).to_numpy()
    return _long_only(entry, out, bars_df.index)


def portfolio_kwargs(**params):
    return {}
