"""Pivot Trend (LonesomeTheBlue): the average percent distance of the close from the last three
pivot lows and from two of the last three pivot highs; both positive turns the trend up (long),
both negative turns it down (short).
Port of FMZ strategy #366936 "Pivot Trend".

Source
    https://www.fmz.com/strategy/366936 (PineScript v4, FMZ last modified 2022-05-31 18:43:20).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 59-106), pivot period 4, number of pivots 3
    pl_lev / ph_lev = the last 3 confirmed pivot lows / highs (na until filled)
    lrate = sum over the 3 pivot lows of (close - pl) / pl / 3
    hrate = sum over pivot highs 2 and 3 (the newest is skipped, loop from i = 1) / 3
    trend = hrate > 0 and lrate > 0 ? 1 : hrate < 0 and lrate < 0 ? -1 : trend[1]
    change(trend) > 0 -> entry long; else change(trend) < 0 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The hrate loop starting at 1 (skipping the newest pivot high) is kept as written. Rates
      are na until every slot is filled.
    * Pivots are confirmed 4 bars after the pivot bar (no look-ahead); a 0 pivot counts as none.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_366936_pivot_distance_trend"
FAMILY = "pivot_reversal"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "prd": [3, 4, 6],
    "pnum": [3, 5],
}
DEFAULT_PARAMS = {"prd": 4, "pnum": 3}


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
    prd, k = int(p["prd"]), int(p["pnum"])
    ph = _pivots(bars_df["high"], prd, prd, True)
    pl = _pivots(bars_df["low"], prd, prd, False)
    c = bars_df["close"].to_numpy(dtype=float)
    m = len(c)
    hl, ll = [np.nan] * k, [np.nan] * k
    trend = np.zeros(m)
    t = 0.0
    for i in range(m):
        if not np.isnan(ph[i]) and ph[i] != 0:
            hl = [ph[i]] + hl[:-1]
        if not np.isnan(pl[i]) and pl[i] != 0:
            ll = [pl[i]] + ll[:-1]
        lrate = sum((c[i] - v) / v / k for v in ll)
        hrate = sum((c[i] - v) / v / k for v in hl[1:])
        if hrate > 0 and lrate > 0:
            t = 1.0
        elif hrate < 0 and lrate < 0:
            t = -1.0
        trend[i] = t
    d = np.diff(trend, prepend=0.0)
    return _always_in(d > 0, d < 0, bars_df.index)


def portfolio_kwargs(**params):
    return {}
