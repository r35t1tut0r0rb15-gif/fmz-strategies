"""Dual momentum, hourly bars: the 5-bar and 10-bar momentum both above zero hold a long, both below
zero hold a short; a long closes once either turns negative, a short once either turns positive.
Port of FMZ strategy #428081 "Dual Momentum Strategy" (Momentum Strategy Idea).

FMZ source id: 428081

Source
    https://www.fmz.com/strategy/428081 (PineScript v4, FMZ last modified 2023-09-28 15:03:57).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 169-210), momentum 5 / 10, stop 5 % (off)
    enter long: mom10 > 0 and mom5 > 0; exit long: mom10 < 0 or mom5 < 0; shorts mirror
    stop-loss exits only when "Use Stop-Loss" is on (default off)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Defaults kept: long-only off, stop off.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, momentum signs only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the off stop stored in original_sizing.txt.
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

NAME = "fmz_428081_dual_momentum_sign"
FAMILY = "momentum_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_period": [5, 10],
    "slow_period": [10, 20],
}
DEFAULT_PARAMS = {"fast_period": 5, "slow_period": 10}


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
    c = bars_df["close"]
    f = (c - c.shift(int(p["fast_period"]))).to_numpy()
    s = (c - c.shift(int(p["slow_period"]))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if s[i] > 0 and f[i] > 0:
                pos = 1
            elif s[i] < 0 and f[i] < 0:
                pos = -1
            elif pos == 1 and (s[i] < 0 or f[i] < 0):
                pos = 0
            elif pos == -1 and (s[i] > 0 or f[i] > 0):
                pos = 0
            tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
