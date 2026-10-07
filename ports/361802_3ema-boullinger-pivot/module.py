"""Confirmed pivot low -> long, confirmed pivot high -> short (always in).
Port of FMZ strategy #361802 "3EMA-Boullinger-PIVOT" (JCMR76 indicator, orders added).

Source
    https://www.fmz.com/strategy/361802 (PineScript v4, FMZ last modified 2022-05-08 12:29:27).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 95-103), dist 6
    pl = pivotlow(low, 6, 6);  if not na(pl) -> entry long
    ph = pivothigh(high, 6, 6); if not na(ph) -> entry short
    (three EMAs and Bollinger bands are plotted only)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pivots are confirmed `dist` bars later (no lookahead); strict on both sides.
    * Two separate `if`s: when both pivots confirm on one bar, both entries are sent and the
      later (short) decides the side. strategy.entry reverses: REVERSAL INTENDED
      (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361802_pivot_confirm_side"
FAMILY = "pivot_reversal"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "dist": [3, 6, 10],
}
DEFAULT_PARAMS = {"dist": 6}


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
    n = int(p["dist"])
    pl = ~np.isnan(_pivots(bars_df["low"], n, n, False))
    ph = ~np.isnan(_pivots(bars_df["high"], n, n, True))
    return _always_in(pl, ph, bars_df.index, short_first=True)


def portfolio_kwargs(**params):
    return {}
