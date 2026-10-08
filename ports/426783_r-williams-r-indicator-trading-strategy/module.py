"""Williams %R, long only: %R(14) crossing above -80 goes long; crossing under -20 closes the long.
Port of FMZ strategy #426783 "Williams R Indicator Trading Strategy".

Source
    https://www.fmz.com/strategy/426783 (PineScript v5, FMZ last modified 2023-09-14 15:38:51).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 120-137), length 14, -20 / -80
    wr = -100 * (highest(high, 14) - close) / (highest(high, 14) - lowest(low, 14))
    crossover(wr, -80) -> entry long;  crossunder(wr, -20) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only (no short entry).
    * FREQ = "12h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426783_williams_r_long"
FAMILY = "williams_r_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "12h"  # backtest header period: 12h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [7, 14, 21],
    "oversold": [-80, -90],
}
DEFAULT_PARAMS = {"length": 14, "overbought": -20, "oversold": -80}


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
    n = int(p["length"])
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hh, ll = h.rolling(n).max(), l.rolling(n).min()
    wr = -100 * (hh - c) / (hh - ll)
    w1 = wr.shift(1)
    le = (wr > p["oversold"]) & (w1 <= p["oversold"])
    lx = (wr < p["overbought"]) & (w1 >= p["overbought"])
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
