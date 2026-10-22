"""Close crossing its SMA 500, 1-hour bars: the close crossing over goes long, under goes short; reversing (the closes repeat the reversals).
Port of FMZ strategy #442959 "Trend Tracking Strategy Based on Moving Average" (Una AI Strategy).

FMZ source id: 442959

Source
    https://www.fmz.com/strategy/442959 (PineScript v5, FMZ last modified 2024-02-27 16:29:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 122-152), SMA 500
    close > sma and close[1] <= sma -> entry Buy, close Sell;  close < sma and close[1] >= sma -> entry Sell, close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The crossing compares the previous close with the current SMA, as written. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close vs SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_442959_close_sma500_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_period": [500, 200],
}
DEFAULT_PARAMS = {"sma_period": 500}


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
    s = c.rolling(int(p["sma_period"])).mean()
    le = (c > s) & (c.shift(1) <= s)
    se = (c < s) & (c.shift(1) >= s)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
