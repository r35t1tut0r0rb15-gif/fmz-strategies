"""Leledec exhaustion bars, 2-hour bars: a major bullish exhaustion (more than 6 closes below the close 4 bars earlier, then
a green bar at the 30-bar low) goes long; a minor bearish exhaustion (more than 5 closes above, then a red bar at the
5-bar high) goes short.
Port of FMZ strategy #430651 "DEC策略Leledec-DEC-Strategy" (A Strategy for Leledec).

FMZ source id: 430651

Source
    https://www.fmz.com/strategy/430651 (PineScript v4, FMZ last modified 2023-10-31 11:47:00).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 174-254), major 6 / 30, minor 5 / 5, close look-back 4
    lele(qual, len): bindex / sindex count closes above / below close[4]
      bindex > qual and red bar and high >= highest(high, len) -> ret -1, bindex := 0
      sindex > qual and green bar and low <= lowest(low, len) -> ret 1, sindex := 0
    major = lele(6, 30); minor = lele(5, 5)
    major == 1 -> entry long;  minor == -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The counters carry over bars (bindexSindex = 1: the value one bar back) and reset only when
      their exhaustion fires, as written; each lele call keeps its own counters. The buy uses the
      major setting and the sell the minor one, as written.
    * The 2018-2030 window is the author's backtest window: dropped. strategy.entry reverses:
      REVERSAL INTENDED. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close counts and bar extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity per entry stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430651_leledec_exhaustion"
FAMILY = "td_sequential"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "maj_qual": [6, 9],
    "maj_len": [30, 20],
}
DEFAULT_PARAMS = {"maj_qual": 6, "maj_len": 30, "min_qual": 5, "min_len": 5, "close_val": 4}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _lele(bars, qual, length, cv_n):
    o, h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    hh = bars["high"].rolling(length).max().to_numpy()
    ll = bars["low"].rolling(length).min().to_numpy()
    m = len(c)
    out = np.zeros(m, dtype=np.int8)
    b = s = 0
    for i in range(m):
        if i >= cv_n:
            if c[i] > c[i - cv_n]:
                b += 1
            if c[i] < c[i - cv_n]:
                s += 1
        r = 0
        if b > qual and c[i] < o[i] and h[i] >= hh[i]:
            b, r = 0, -1
        if s > qual and c[i] > o[i] and lo[i] <= ll[i]:
            s, r = 0, 1
        out[i] = r
    return out


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
    n = int(p["close_val"])
    major = _lele(bars_df, int(p["maj_qual"]), int(p["maj_len"]), n)
    minor = _lele(bars_df, int(p["min_qual"]), int(p["min_len"]), n)
    m = len(major)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if major[i] == 1:
            pos = 1
        if minor[i] == -1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
