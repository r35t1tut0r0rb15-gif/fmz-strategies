"""Gann swing oscillator (HPotter, always in): a fresh 3-bar swing high in the highest close turns
the oscillator to -1 (short); a fresh swing low in the lowest close turns it to +1 (long).
Port of FMZ strategy #426883 "Quantitative Trading Strategy Based on Gann Swing Oscillator".

Source
    https://www.fmz.com/strategy/426883 (PineScript v2/v3 syntax, FMZ last modified 2023-09-15 11:37:37).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 131-145), Length 3
    hh = highest(close, 3); ll = lowest(close, 3)
    gso = hh[2] > hh[1] and hh > hh[1] ? -1 : ll[2] < ll[1] and ll < ll[1] ? 1 : gso[1]
    gso > 0 -> entry long;  gso < 0 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The -1 test comes first, as in the source. "Trade reverse" off.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "3h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426883_gann_swing_oscillator"
FAMILY = "pivot_reversal"  # proposed 2026-10-07, user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [3, 5, 8],
}
DEFAULT_PARAMS = {"length": 3}


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
    n = int(p["length"])
    hh, ll = c.rolling(n).max(), c.rolling(n).min()
    down = ((hh.shift(2) > hh.shift(1)) & (hh > hh.shift(1))).to_numpy()
    up = ((ll.shift(2) < ll.shift(1)) & (ll < ll.shift(1))).to_numpy()
    return _always_in(up, down, bars_df.index, short_first=True)


def portfolio_kwargs(**params):
    return {}
