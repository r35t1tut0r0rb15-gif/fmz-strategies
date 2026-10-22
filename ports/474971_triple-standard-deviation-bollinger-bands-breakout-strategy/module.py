"""Asymmetric Bollinger breakouts, hourly bars, long only: from flat, a close over SMA 100 + 3 standard deviations buys; a close under SMA 100 - 1 standard deviation sells.
Port of FMZ strategy #474971 "Triple Standard Deviation Bollinger Bands Breakout Strategy with 100 Day Moving Average Optimization" (Bollinger Bands).

FMZ source id: 474971

Source
    https://www.fmz.com/strategy/474971 (PineScript v6, FMZ last modified 2024-12-13 11:20:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-152), SMA 100; upper 3 sd, lower 1 sd; 200 % of equity
    close > bb(100, 3).upper and flat -> entry Trade;  close < bb(100, 1).lower and in position -> close Trade

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry and close tests cannot hold on one bar; a repeat entry while long would be ignored.
      barstate.isconfirmed holds on every historical bar. The backtester table is commented out. Long
      only. The equity share is not ported. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, asymmetric band breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
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

NAME = "fmz_474971_sma100_3sd_breakout_1sd_exit_long"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "upper_sd": [3.0, 2.0],
    "ma_period": [100, 50],
}
DEFAULT_PARAMS = {"upper_sd": 3.0, "ma_period": 100, "lower_sd": 1.0}


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
    n = int(p["ma_period"])
    mid, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    le = c > mid + float(p["upper_sd"]) * sd
    lx = c < mid - float(p["lower_sd"]) * sd
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
