"""Swing-pivot side as written: a confirmed swing HIGH of the close goes long, a confirmed
swing LOW of the open goes short (always in).
Port of FMZ strategy #361718 "Swing-Highs-Lows-Candle-Patterns" (LuxAlgo, orders added).

Source
    https://www.fmz.com/strategy/361718 (PineScript v4, FMZ last modified 2022-05-07 21:35:09).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 62-112), length 21
    ph = pivothigh(close, 21, 21); pl = pivotlow(open, 21, 21)
    if ph -> entry long;  else if pl -> entry short
    (candle patterns and HH/LL labels are display only)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pivots are confirmed `length` bars after the centre bar (no lookahead). Pivot test strict
      on both sides. `if ph` is true when a pivot value exists.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}; the engine's default
      opposite-entry reversal applies).
    * FREQ = "2h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361718_swing_pivot_side"
FAMILY = "pivot_reversal"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 21, 34],
}
DEFAULT_PARAMS = {"length": 21}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _pivots(x, left, right, high):
    """ta.pivothigh/pivotlow(x, left, right): value of the pivot confirmed on each bar (NaN if
    none); the centre bar t-right strictly beyond the `left` bars before and `right` bars after."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    for t in range(left + right, len(v)):
        c = t - right
        side = np.concatenate([v[c - left:c], v[c + 1:t + 1]])
        if np.isnan(v[c]) or np.isnan(side).any():
            continue
        if (high and v[c] > side.max()) or (not high and v[c] < side.min()):
            out[t] = v[c]
    return out


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
    n = int(p["length"])
    ph = ~np.isnan(_pivots(bars_df["close"], n, n, True))
    pl = ~np.isnan(_pivots(bars_df["open"], n, n, False))
    return _always_in(ph, pl, bars_df.index)


def portfolio_kwargs(**params):
    return {}
