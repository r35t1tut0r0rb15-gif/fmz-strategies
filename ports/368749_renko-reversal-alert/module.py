"""Renko reversal alert (Zer3192): a close above the previous open after a close below the open two
bars back goes long; the mirror goes short (always in).
Port of FMZ strategy #368749 "Renko Reversal alert".

Source
    https://www.fmz.com/strategy/368749 (PineScript v4, author Zer3192, FMZ last modified
    2022-06-12 18:32:42). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 28-41)
    long  = close > open[1] and close[1] < open[2]
    short = close < open[1] and close[1] > open[2]
    long -> entry long; else short -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Meant for Renko charts; ported on the backtest header's time bars (4h) as the source runs.
    * No parameters (1 trial). strategy.entry reverses: REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_368749_bar_reversal_pattern"
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
    long_ = ((c > o.shift(1)) & (c.shift(1) < o.shift(2))).to_numpy()
    short = ((c < o.shift(1)) & (c.shift(1) > o.shift(2))).to_numpy()
    return _always_in(long_, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
