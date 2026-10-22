"""One bar a day at 14:00 UTC, 1-hour bars, long only: a green 14:00 UTC bar goes long, a red one closes.
Port of FMZ strategy #440562 "坎普敦15分钟蜡烛突破策略Cape-Town-15-min-Candle-Breakout-Strategy" (Cape Town 15-Min Candle Strategy).

FMZ source id: 440562

Source
    https://www.fmz.com/strategy/440562 (PineScript v5, FMZ last modified 2024-01-31 17:15:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 124-150), time test hour + 2 == 16 and minute 0-14 (Cape Town 16:00)
    isInTimeRange = hour + 2 == 16 and minute <= 14;  close > open and in range -> entry Buy;  close < open and in range -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * hour and minute are read on the UTC bar open: on 1-hour bars only the 14:00 UTC bar qualifies (the
      author's 15-minute bar is not the declared chart). Long only. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle colour at a fixed hour.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: the bar opening 14:00 UTC (bar open time).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440562_cape_town_1400_candle_long"
FAMILY = "calendar_seasonal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "utc_hour": [14, 13],
}
DEFAULT_PARAMS = {"utc_hour": 14}


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
    o, c = bars_df["open"], bars_df["close"]
    ix = bars_df.index.tz_convert("UTC")
    t = pd.Series((ix.hour == int(p["utc_hour"])) & (ix.minute <= 14), index=c.index)
    buy = (c > o) & t
    sell = (c < o) & t
    false = pd.Series(False, index=c.index)
    return buy, sell, false, false.copy()


def portfolio_kwargs(**params):
    return {}
