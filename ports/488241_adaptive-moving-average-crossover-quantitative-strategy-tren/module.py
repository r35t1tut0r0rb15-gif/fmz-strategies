"""SMA 9 / 21 crossings, 2-hour bars, long only: the up-cross goes long, the down-cross closes.
Port of FMZ strategy #488241 "Adaptive Moving Average Crossover Quantitative Strategy Trend Following and Trading Signal Optimization" (Moving Average Crossover Strategy).

FMZ source id: 488241

Source
    https://www.fmz.com/strategy/488241 (PineScript v5, FMZ last modified 2025-03-26 11:09:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 195-236), SMA 9 / 21 (type SMA)
    crossover(fastMA, slowMA) -> entry Long Entry;  crossunder(fastMA, slowMA) -> close Long Entry

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only. No sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488241_sma9_21_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fastLength": [9, 5],
    "slowLength": [21, 50],
}
DEFAULT_PARAMS = {"fastLength": 9, "slowLength": 21}


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
    f, s = c.rolling(int(p["fastLength"])).mean(), c.rolling(int(p["slowLength"])).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    lx = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
