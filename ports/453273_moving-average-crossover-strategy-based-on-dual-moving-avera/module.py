"""SMA 9 / 21 crossings, 1-hour bars, long only: the cross up buys, the cross down sells.
Port of FMZ strategy #453273 "Moving Average Crossover Strategy Based on Dual Moving Averages" (Moving Average Crossover Strategy (SMA 9 / 21)).

FMZ source id: 453273

Source
    https://www.fmz.com/strategy/453273 (PineScript v5, FMZ last modified 2024-06-03 16:39:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-130), SMA 9 / 21; quantity 1 (the capital / risk inputs only feed a label)
    crossover(sma9, sma21) -> entry Buy (qty 1);  crossunder -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The risk-based size is computed but the entry uses qty = 1; both are sizing. Long only. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity 1 stored.
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

NAME = "fmz_453273_sma9_21_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [9, 5],
    "long_len": [21, 50],
}
DEFAULT_PARAMS = {"short_len": 9, "long_len": 21}


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
    a = c.rolling(int(p["short_len"])).mean()
    b = c.rolling(int(p["long_len"])).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1))
    lx = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
