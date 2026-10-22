"""EMA 9 / 21 crossings, hourly bars, long only: the up-cross goes long from flat, the down-cross closes.
Port of FMZ strategy #483495 "Dynamic Dual Moving Average Crossover Strategy with Single Trade Execution System using Exponential Moving Averages" (EMA Crossover Labels (One Trade at a Time)).

FMZ source id: 483495

Source
    https://www.fmz.com/strategy/483495 (PineScript v6, FMZ last modified 2025-02-24 09:15:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-133), EMA 9 / 21; "Strategy Timeframe" 10 (unused); 10 % of equity, capital 100000
    crossover(ema9, ema21) and flat -> entry Long;  crossunder(ema9, ema21) and long -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The crossings alternate, so the flat / long gates always hold when a crossing comes. The timeframe
      input feeds nothing (the header's 1h is the bar size). Long only. The 10 % of equity size and the
      capital are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity and capital stored, not ported.
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

NAME = "fmz_483495_ema9_21_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_period9": [9, 5],
    "ema_period21": [21, 50],
}
DEFAULT_PARAMS = {"ema_period9": 9, "ema_period21": 21}


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
    f = c.ewm(span=int(p["ema_period9"]), adjust=False).mean()
    s = c.ewm(span=int(p["ema_period21"]), adjust=False).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    lx = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
