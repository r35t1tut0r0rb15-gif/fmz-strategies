"""Candle strength (Zer3192): a green candle goes long, a red candle goes short (always in); the
close-in-range percentages only label the bars.
Port of FMZ strategy #380219 "Candle Strength".

Source
    https://www.fmz.com/strategy/380219 (PineScript v5, author Zer3192, FMZ last modified
    2022-08-27 12:03:45). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 46-56)
    close > open -> entry long; else open > close -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry lines are oddly indented (1 / 5 spaces) but sit in their if / else-if blocks as the
      FMZ runtime executes them. No parameters (1 trial).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_380219_candle_colour_follow"
FAMILY = "candle_pattern"  # proposed 2026-10-07, user to confirm
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
    o, c = bars_df["open"], bars_df["close"]
    return _always_in((c > o).to_numpy(), (o > c).to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
