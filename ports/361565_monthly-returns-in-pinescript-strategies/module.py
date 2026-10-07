"""Pivot "reversal" with market orders: after a confirmed pivot high, go long until price trades
above it; after a confirmed pivot low, go short until price trades below it.
Port of FMZ strategy #361565 "Monthly-Returns-in-PineScript-Strategies" (the pivot reversal
example strategy that carries the monthly-returns table).

Source
    https://www.fmz.com/strategy/361565 (PineScript v4, FMZ last modified 2022-05-08 10:43:41).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 52-76), leftBars 2, rightBars 2
    swh = pivothigh(2, 2); swl = pivotlow(2, 2)
    hprice := swh if found else hprice[1];  lprice likewise
    le := swh found ? true : (le[1] and high > hprice ? false : le[1])
    se := swl found ? true : (se[1] and low < lprice ? false : se[1])
    if le -> entry long;  if se -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The well-known original places these entries as stop orders (stop = pivot +/- tick); this
      script has no stop= argument, so they are market orders at the next open, as written.
    * A pivot is confirmed rightBars bars later (no lookahead). Pivot test: the centre bar's high
      strictly above the leftBars before and the rightBars after it (lows mirror).
    * Both flags true on one bar: both entries are sent and the later (short) one decides the
      final side. strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * The strategy() line (with calc_on_every_tick) is commented out in the source, so FMZ's
      defaults apply. FREQ = "12h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361565_pivot_flag_market_reverse"
FAMILY = "pivot_reversal"  # proposed 2026-10-07, user to confirm
FREQ = "12h"  # backtest header period: 12h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "left_bars": [2, 3, 5],
    "right_bars": [1, 2, 3],
}
DEFAULT_PARAMS = {"left_bars": 2, "right_bars": 2}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _pivots(x, left, right, high):
    """Value of the pivot confirmed on each bar (NaN if none): centre bar t-right strictly
    beyond the `left` bars before it and the `right` bars after it."""
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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lb, rb = int(p["left_bars"]), int(p["right_bars"])
    h, lo = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    swh = _pivots(bars_df["high"], lb, rb, True)
    swl = _pivots(bars_df["low"], lb, rb, False)

    m = len(h)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    hprice = lprice = 0.0
    lflag = sflag = False
    pos = 0
    for i in range(m):
        if not np.isnan(swh[i]):
            hprice, lflag = swh[i], True
        elif lflag and h[i] > hprice:
            lflag = False
        if not np.isnan(swl[i]):
            lprice, sflag = swl[i], True
        elif sflag and lo[i] < lprice:
            sflag = False
        target = -1 if sflag else (1 if lflag else pos)
        if target == 1 and pos != 1:
            le[i], pos = True, 1
        elif target == -1 and pos != -1:
            se[i], pos = True, -1

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
