"""SMA 50 / SMA 200 golden and death crosses, hourly bars: the golden cross goes long, the death cross goes short.
Port of FMZ strategy #428986 "Golden Cross Death Cross Strategy" (Golden X BF Strategy).

FMZ source id: 428986

Source
    https://www.fmz.com/strategy/428986 (PineScript v4, FMZ last modified 2023-10-11 16:33:18).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 183-236), SMA 50 / 200 on close
    crossover(sma(close,50), sma(close,200)) -> entry long; crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The MA type inputs default to SMA (EMA / SWMA / WMA are options). The test period is dropped
      (testPeriod is true). The strategy() line is commented out.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crosses only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out strategy() stored.
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

NAME = "fmz_428986_sma50_200_golden_cross"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length1": [50, 20],
    "length2": [200, 100],
}
DEFAULT_PARAMS = {"length1": 50, "length2": 200}


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
    f, s = c.rolling(int(p["length1"])).mean(), c.rolling(int(p["length2"])).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
