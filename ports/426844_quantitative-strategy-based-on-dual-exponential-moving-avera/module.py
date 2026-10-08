"""EMA 29 / 86 state (always in): long while EMA 29 is above EMA 86, short while below.
Port of FMZ strategy #426844 "Quantitative Strategy Based on Dual Exponential Moving Average".

Source
    https://www.fmz.com/strategy/426844 (PineScript v4, FMZ last modified 2023-09-14 19:51:37).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 127-139), EMA 29 / 86
    ema29 > ema86 -> entry long;  ema29 < ema86 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426844_ema_29_86_state"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "small_ema": [20, 29],
    "long_ema": [86, 120],
}
DEFAULT_PARAMS = {"small_ema": 29, "long_ema": 86}


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
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    d = c.ewm(span=int(p["small_ema"]), adjust=False).mean() - c.ewm(span=int(p["long_ema"]), adjust=False).mean()
    return _always_in((d > 0).to_numpy(), (d < 0).to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
