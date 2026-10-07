"""Confirmed pivot low -> long, confirmed pivot high -> short (always in); the order-block boxes
are drawing only.
Port of FMZ strategy #362542 "Pivot-Order-Blocks".

Source
    https://www.fmz.com/strategy/362542 (PineScript v5, FMZ last modified 2022-05-11 23:35:28).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 67-118), pivots 10/10
    ph = pivothigh(10, 10); pl = pivotlow(10, 10)
    if pl -> entry long;  else if ph -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pivots are confirmed 10 bars later (no lookahead); strict on both sides.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * No backtest header: FREQ = "bar_size_pending" (rule 1).

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_362542_pivot_side_10"
FAMILY = "pivot_reversal"  # proposed 2026-10-07, user to confirm
FREQ = "bar_size_pending"  # source declares no bar size; set by the project before running
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "left": [5, 10, 20],
    "right": [5, 10],
}
DEFAULT_PARAMS = {"left": 10, "right": 10}


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
    lb, rb = int(p["left"]), int(p["right"])
    pl = ~np.isnan(_pivots(bars_df["low"], lb, rb, False))
    ph = ~np.isnan(_pivots(bars_df["high"], lb, rb, True))
    return _always_in(pl, ph, bars_df.index)


def portfolio_kwargs(**params):
    return {}
