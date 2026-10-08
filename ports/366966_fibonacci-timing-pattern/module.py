"""Fibonacci timing pattern (Zer3192): eight consecutive closes each below the closes 3 and 5 bars
earlier (with the turn condition close[8] > close[11]) goes long; the mirror goes short.
Port of FMZ strategy #366966 "Fibonacci Timing Pattern".

Source
    https://www.fmz.com/strategy/366966 (PineScript v5, author Zer3192, FMZ last modified
    2022-05-31 21:25:21). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 31-63)
    FB_Buy = close[j] < close[j + 3] and close[j] < close[j + 5] for j = 0..7, and close[8] > close[11]
    FB_Sell mirrors
    FB_Buy -> entry long; else FB_Sell -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "if FB_Buy and FB_Buy[1]: FB_Buy == false" is a comparison, not an assignment: no effect.
    * No parameters reach the orders (1 trial).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_366966_fibonacci_timing_pattern"
FAMILY = "td_sequential"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    c = bars_df["close"]
    s = lambda k: c.shift(k)
    buy = s(8) > s(11)
    sell = s(8) < s(11)
    for j in range(8):
        buy &= (s(j) < s(j + 3)) & (s(j) < s(j + 5))
        sell &= (s(j) > s(j + 3)) & (s(j) > s(j + 5))
    return _always_in(buy.to_numpy(), sell.to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
