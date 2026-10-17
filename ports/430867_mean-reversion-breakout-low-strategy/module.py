"""Broken-low mean reversion (merovinh), 1-hour bars, long only: a new, lower 9-bar lowest low (below the previous distinct
lowest-low value) goes long; a new, higher 9-bar highest high closes the long.
Port of FMZ strategy #430867 "Mean Reversion Breakout Low Strategy" (Merovinh - Mean Reversion Lowest low).

FMZ source id: 430867

Source
    https://www.fmz.com/strategy/430867 (PineScript v5, FMZ last modified 2023-11-02 15:34:22).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 156-214), 9 bars, one broken low
    prevLow > 0 and lowest(low, 9) < prevLow -> entry long
    prevHigh > 0 and highest(high, 9) > prevHigh -> close long
    after the orders: prevLow := lowest(low, 9) when it changed (older values shift back); prevHigh := highest(high, 9)

Interpretation choices (Pine rules in SURVEY_README.md)
    * prevLow is the previous distinct 9-bar lowest low and prevHigh the previous bar's 9-bar highest
      high, both updated after the orders, as written. Default "One" broken low.
    * The close is written after the entry: a bar that both qualifies and closes ends flat when
      already long, long when flat. Long only; Opposite entries cannot occur. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, rolling extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity per entry stored in original_sizing.txt.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430867_broken_low_reversion_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bars": [9, 20, 5],
}
DEFAULT_PARAMS = {"bars": 9}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["bars"])
    hh = bars_df["high"].rolling(n).max().to_numpy()
    ll = bars_df["low"].rolling(n).min().to_numpy()
    m = len(hh)
    tgt = np.zeros(m, dtype=np.int8)
    pos, prev_low, prev_high = 0, 0.0, 0.0
    for i in range(m):
        start = pos
        if prev_low > 0 and ll[i] < prev_low:
            pos = 1
        if start == 1 and prev_high > 0 and hh[i] > prev_high:
            pos = 0
        if not np.isnan(ll[i]) and prev_low != ll[i]:
            prev_low = ll[i]
        prev_high = 0.0 if np.isnan(hh[i]) else hh[i]
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
