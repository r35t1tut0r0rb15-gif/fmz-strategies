"""Fair value gaps, 1-hour bars: a bearish gap (the high under the low two bars back, with the previous close also under it) goes short, otherwise a bullish gap (the low above the high two bars back, the
previous close above it) goes long; reversing.
Port of FMZ strategy #442257 "Breakthrough Fair Value Gap Strategy" (FVG Strategy).

FMZ source id: 442257

Source
    https://www.fmz.com/strategy/442257 (PineScript v5, FMZ last modified 2024-02-20 15:47:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-138), long only off; pyramiding 1; 100 % of equity
    high < low[2] and close[1] < low[2] -> entry Short;  else low > high[2] and close[1] > high[2] -> entry Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bearish test is checked first, as written. pyramiding = 1 allows one entry per direction, so a
      gap in the held direction does nothing. strategy.entry reverses: REVERSAL INTENDED. The 100 % of
      equity size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, three-bar gap tests.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442257_fair_value_gap_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "gap_back": [2, 3],
}
DEFAULT_PARAMS = {"gap_back": 2}


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
    k = int(p["gap_back"])
    bear = (h < lo.shift(k)) & (c.shift(1) < lo.shift(k))
    bull = (lo > h.shift(k)) & (c.shift(1) > h.shift(k)) & ~bear
    false = pd.Series(False, index=c.index)
    return bull, false, bear, false.copy()


def portfolio_kwargs(**params):
    return {}
