"""Golden cross, long only: SMA 50 crossing above SMA 200 goes long; crossing below closes it.
Port of FMZ strategy #426925 "Golden Cross Strategy".

Source
    https://www.fmz.com/strategy/426925 (PineScript v2/v3 syntax, FMZ last modified 2023-09-15 15:50:20).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 145-167), SMA 50 / 200
    crossover(sma50, sma200) -> entry long;  crossunder -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only. FREQ = "2min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426925_golden_cross_long"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 50],
    "slow": [100, 200],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200}


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
    d = c.rolling(int(p["fast"])).mean() - c.rolling(int(p["slow"])).mean()
    d1 = d.shift(1)
    le = (d > 0) & (d1 <= 0)
    lx = (d < 0) & (d1 >= 0)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
