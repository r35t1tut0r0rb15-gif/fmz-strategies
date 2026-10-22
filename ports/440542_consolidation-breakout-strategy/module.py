"""Bollinger band breakouts, 1-hour bars: the close crossing over the upper band (20, 2) goes long, crossing under the lower band goes short; reversing (the written closes name entries that do not exist).
Port of FMZ strategy #440542 "Consolidation Breakout Strategy" (CBS).

FMZ source id: 440542

Source
    https://www.fmz.com/strategy/440542 (PineScript v5, FMZ last modified 2024-01-31 15:08:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 135-172), BB 20 / 2; risk 1 % (unused); ATR 14 x 2 (stop distance, unused by the orders)
    breakout = crossover(close, upper) or crossunder(close, lower);  breakout and close > upper -> entry Long;  breakout and close < lower -> entry Short
    strategy.close("Long Exit") / ("Short Exit") on further tests: ids never entered, nothing closes

Interpretation choices (Pine rules in SURVEY_README.md)
    * The consolidation test (crossing over the upper and under the lower band together) can never be
      true and only feeds a plot. The close calls name ids that are never entered and do nothing. Pine's
      stdev is the population deviation. strategy.entry reverses: REVERSAL INTENDED. No sizing code (the
      risk input is unused). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger band crossings.
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

NAME = "fmz_440542_bollinger_band_breakout_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, lo = basis + dev, basis - dev
    lg = (c > up) & (c.shift(1) <= up.shift(1))
    sh = (c < lo) & (c.shift(1) >= lo.shift(1))
    false = pd.Series(False, index=c.index)
    return lg, false, sh, false.copy()


def portfolio_kwargs(**params):
    return {}
