"""SMA 20 / 50 crossings, 3-minute bars: the fast SMA crossing over the slow one goes long (closing a short); crossing under goes short (closing a long), so the position reverses.
Port of FMZ strategy #436254 "Moving Average Crossover Long Short Trading Strategy" (Il mio script (SMA cross)).

FMZ source id: 436254

Source
    https://www.fmz.com/strategy/436254 (PineScript v5, FMZ last modified 2023-12-22 15:13:50).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 109-126), SMA 20 / 50
    bullishCrossover -> entry long, close short;  bearishCrossover -> entry short, close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The explicit closes coincide with the reversal. REVERSAL INTENDED. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crossings.
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

NAME = "fmz_436254_sma_20_50_cross_3min"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    le = ((f > s) & (f.shift(1) <= s.shift(1))).fillna(False).astype(bool)
    se = ((f < s) & (f.shift(1) >= s.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
