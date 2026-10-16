"""Bollinger basis cross, 3-hour bars: the close crossing above the SMA 20 goes long, crossing below goes short.
Port of FMZ strategy #429561 "双线性BB口系统策略Dual-Moving-Average-Bollinger-Band-System-Strategy" (BB돌파).

FMZ source id: 429561

Source
    https://www.fmz.com/strategy/429561 (PineScript v5, FMZ last modified 2023-10-18 11:01:19).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 227-245), length 20, stdev 2 (the bands are drawn only)
    crossover(close, sma(close,20)) -> entry long; crossunder(close, sma(close,20)) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the basis is traded; the bands are drawn. strategy.entry reverses: REVERSAL INTENDED.
      FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a moving-average cross only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: ND427162 (2 members, best partner #427162, Jaccard 0.683); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429561_bb_basis_cross"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
}
DEFAULT_PARAMS = {"length": 20}


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
    b = c.rolling(int(p["length"])).mean()
    long_e = ((c > b) & (c.shift(1) <= b.shift(1))).astype(bool)
    short_e = ((c < b) & (c.shift(1) >= b.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
