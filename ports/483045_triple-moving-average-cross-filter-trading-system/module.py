"""SMA 21 / 50 crossings on the SMA 100 side, hourly bars, long only: an up-cross with both averages over the SMA 100 goes long, a down-cross with both under it closes.
Port of FMZ strategy #483045 "Triple Moving Average Cross Filter Trading System" (Vezpa's Gold Strategy).

FMZ source id: 483045

Source
    https://www.fmz.com/strategy/483045 (PineScript v5, FMZ last modified 2025-02-21 10:48:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 127-176), SMA 21 / 50; trend SMA 100; MPL 2.0 notice (Vezpa)
    crossover(sma21, sma50) and sma21 > sma100 and sma50 > sma100 -> entry Buy;  crossunder(sma21, sma50) and both < sma100 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only. No sizing code. The MPL 2.0 notice is kept with the verbatim copy (ported, stated).
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with a trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
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

NAME = "fmz_483045_sma21_50_cross_sma100_filter_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_length": [21, 10],
    "trend_filter_length": [100, 200],
}
DEFAULT_PARAMS = {"fast_length": 21, "trend_filter_length": 100, "slow_length": 50}


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
    f = c.rolling(int(p["fast_length"])).mean()
    s = c.rolling(int(p["slow_length"])).mean()
    t = c.rolling(int(p["trend_filter_length"])).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (f > t) & (s > t)
    lx = (f < s) & (f.shift(1) >= s.shift(1)) & (f < t) & (s < t)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
