"""Smoothed average against a shifted channel midpoint, 1-hour bars: an EMA 53 of the SMA 44 of the close crossing over the
131-bar high / low midpoint (raised 0.06 %, taken 14 bars back) goes long; the midpoint crossing back over the average goes
short (reversing).
Port of FMZ strategy #435284 "Moving Average Crossover Midpoint Strategy" (Forex Midpoint Stratejisi For Nasdaq).

FMZ source id: 435284

Source
    https://www.fmz.com/strategy/435284 (PineScript v5, FMZ last modified 2023-12-13 17:38:23).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 182-229), SMA 44 of close, EMA 53 smoothing; midpoint of the 131-bar high and low x 1.0006, shifted 14 bars
    smoothingLine = ema(sma(close, 44), 53);  midtopdeger = (highest(high, 131) + lowest(low, 131)) / 2 x (1 + 0.0006)
    crossover(smoothingLine, midtopdeger[14]) -> entry long;  crossover(midtopdeger[14], smoothingLine) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The method input is EMA by default (the VWMA branch would read volume and is not used).
      strategy.entry reverses: REVERSAL INTENDED. The commented stop rules are off. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average against a channel midpoint.
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

NAME = "fmz_435284_ma_midpoint_cross"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bperiod": [131, 200],
    "shift": [14, 7],
}
DEFAULT_PARAMS = {"bperiod": 131, "shift": 14, "pct": 0.0006, "sma_len": 44, "smooth_len": 53}


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
    line = c.rolling(int(p["sma_len"])).mean().ewm(span=int(p["smooth_len"]), adjust=False).mean()
    n = int(p["bperiod"])
    mid = (h.rolling(n).max() + lo.rolling(n).min()) / 2
    top = (mid * float(p["pct"]) + mid).shift(int(p["shift"]))
    le = ((line > top) & (line.shift(1) <= top.shift(1))).fillna(False).astype(bool)
    se = ((top > line) & (top.shift(1) <= line.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
