"""Turtle channel breakouts, 1-hour bars: a high above the previous 20-bar high goes long, a low under the previous 20-bar low goes short (reversing); a low at or under the previous 10-bar low closes a long, a
high at or over the previous 10-bar high closes a short; the 55 / 20 slow system can never add (pyramiding 0).
Port of FMZ strategy #437037 "Turtle Trading Strategy Based on Simple Moving Average" (Turtles).

FMZ source id: 437037

Source
    https://www.fmz.com/strategy/437037 (PineScript v2, FMZ last modified 2023-12-29 16:45:51).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 126-162), fast 20 / 10, slow 55 / 20
    enterL1 = high > highest(20)[1], exitL1 = low <= lowest(10)[1], enterS1 = low < lowest(20)[1], exitS1 = high >= highest(10)[1];  slow system the same with 55 / 20
    entry fast L / fast S, close fast L / fast S;  entry slow L / slow S, close slow L / slow S

Interpretation choices (Pine rules in SURVEY_README.md)
    * A slow breakout is always also a fast breakout on the same bar, and with pyramiding 0 the slow
      entry can never fill once the fast one has: the slow system is unreachable and left out (as #436543).
      Orders follow the script's call order: the two entries in turn (an outside bar that breaks both
      ways ends short), then the closes, which only close a position open at the bar's close and left
      unchanged by the entries. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_437037_turtle_fast_channels"
FAMILY = "donchian_breakout"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "enter_fast": [20, 30],
    "exit_fast": [10, 15],
}
DEFAULT_PARAMS = {"enter_fast": 20, "exit_fast": 10}


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
    p = {**DEFAULT_PARAMS, **params}
    h, lo = bars_df["high"], bars_df["low"]
    ne, nx = int(p["enter_fast"]), int(p["exit_fast"])
    el = (h > h.rolling(ne).max().shift(1)).to_numpy()
    es = (lo < lo.rolling(ne).min().shift(1)).to_numpy()
    xl = (lo <= lo.rolling(nx).min().shift(1)).to_numpy()
    xs = (h >= h.rolling(nx).max().shift(1)).to_numpy()
    m = len(el)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if el[i] and new != 1:
            new = 1
        if es[i] and new != -1:
            new = -1
        if new == pos:
            if xl[i] and pos == 1:
                new = 0
            elif xs[i] and pos == -1:
                new = 0
        if new == 1 and pos != 1:
            le[i] = True
        elif new == -1 and pos != -1:
            se[i] = True
        elif new == 0 and pos == 1:
            lx[i] = True
        elif new == 0 and pos == -1:
            sx[i] = True
        pos = new
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
