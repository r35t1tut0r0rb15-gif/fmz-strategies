"""Smoothed short-vs-long cost deviation, 1-hour bars: the 5-bar SMA of (5-bar high-low midpoint minus the SMA 20) above zero goes long, below zero goes short; reversing.
Port of FMZ strategy #442207 "Trend Following Strategy Based on Smoothed Deviation" (Trend-Following Indicator).

FMZ source id: 442207

Source
    https://www.fmz.com/strategy/442207 (PineScript v5, FMZ last modified 2024-02-20 11:15:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 148-187), short term 5, long term 20, smoothing 5, threshold 0
    deviation = (highest(high, 5) + lowest(low, 5)) / 2 - sma(close, 20);  smoothed = sma(deviation, 5);  smoothed > 0 -> entry Long;  smoothed < 0 -> entry Short  (the inner closes never fire on their own block)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Inside each block the close needs the opposite condition, which cannot hold at the same time, so
      only the entries act. The conditions are levels; an entry while already in that direction does
      nothing. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed deviation sign.
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

NAME = "fmz_442207_smoothed_cost_deviation_sign_reversal"
FAMILY = "trend_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_term": [5, 10],
    "long_term": [20, 50],
}
DEFAULT_PARAMS = {"short_term": 5, "long_term": 20, "smooth": 5, "threshold": 0.0}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k = int(p["short_term"])
    dev = (h.rolling(k).max() + lo.rolling(k).min()) / 2 - c.rolling(int(p["long_term"])).mean()
    sd = dev.rolling(int(p["smooth"])).mean()
    th = float(p["threshold"])
    le, se = sd > th, sd < -th
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
