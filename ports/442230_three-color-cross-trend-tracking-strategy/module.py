"""Three-line strike after a pullback bar, 3-hour bars: three green candles, a red one, then a close above its high go long; three red candles, a green one, then a close under its low go short;
reversing.
Port of FMZ strategy #442230 "Three Color Cross Trend Tracking Strategy" (3 Line Strick).

FMZ source id: 442230

Source
    https://www.fmz.com/strategy/442230 (PineScript v5, FMZ last modified 2024-02-20 14:19:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-127), no inputs; margin 100 / 100
    long = close > high[1] and close[1] < open[1] and close[2..4] > open[2..4] -> entry Long;  short = close < low[1] and close[1] > open[1] and close[2..4] < open[2..4] -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are the only orders; positions end at the opposite entry. strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. FREQ = "3h" from the backtest header (bars on UTC multiples of 3
      hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle sequence.
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

NAME = "fmz_442230_three_line_strike_pullback_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "run": [3, 2],
}
DEFAULT_PARAMS = {"run": 3}


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
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    body = c - o
    le = (c > h.shift(1)) & (body.shift(1) < 0)
    se = (c < lo.shift(1)) & (body.shift(1) > 0)
    for k in range(2, 2 + int(p["run"])):
        le &= body.shift(k) > 0
        se &= body.shift(k) < 0
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
