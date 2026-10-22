"""Chande Momentum extremes, 1-hour bars: the CMO 9 crossing back over -80 goes long, crossing back under 80 goes short; reversing.
Port of FMZ strategy #440800 "Single Point Moving Average Breakout Strategy" (ChandeMO Strat).

FMZ source id: 440800

Source
    https://www.fmz.com/strategy/440800 (PineScript v4, FMZ last modified 2024-02-02 11:19:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 135-160), length 9 on close; buy line -80, sell line 80; test period from 2021 (testPeriod() is true)
    cmo = 100 (sum(up moves, 9) - sum(down moves, 9)) / (sum(up, 9) + sum(down, 9));  crossover(cmo, -80) -> entry Long;  crossunder(cmo, 80) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 20 % stop lines are commented out. strategy.entry reverses: REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Chande Momentum crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_440800_chande_momentum_extreme_cross"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [9, 20],
    "buyline": [-80, -50],
}
DEFAULT_PARAMS = {"length": 9, "buyline": -80}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    mom = c.diff()
    s1 = mom.clip(lower=0).rolling(n).sum()
    s2 = (-mom).clip(lower=0).rolling(n).sum()
    tot = s1 + s2
    cmo = 100 * (s1 - s2) / tot.where(tot != 0)
    b = float(p["buyline"])
    s = -b
    up = (cmo > b) & (cmo.shift(1) <= b)
    dn = (cmo < s) & (cmo.shift(1) >= s)
    false = pd.Series(False, index=c.index)
    return up & ~dn, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
