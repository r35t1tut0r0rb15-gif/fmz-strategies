"""Bollinger breakout, long only: the close crossing above the upper band (20, 1.5 sd) goes long;
the close crossing under the middle band goes flat.
Port of FMZ strategy #426339 "Bollinger Band Breakout strategy".

Source
    https://www.fmz.com/strategy/426339 (PineScript v4, FMZ last modified 2023-09-11 12:24:43).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 53-68), period 20, mult 1.5
    basis = sma(close, 20); upper = basis + 1.5 * stdev(close, 20)
    crossover(close, upper) -> entry long;  crossunder(close, basis) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only (no short entry). stdev is Pine's population deviation.
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426339_bollinger_breakout_long"
FAMILY = "bollinger_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20],
    "mult": [1.5, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 1.5}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    c = bars_df["close"]
    basis = c.rolling(n).mean()
    upper = basis + p["mult"] * c.rolling(n).std(ddof=0)
    le = (c > upper) & (c.shift(1) <= upper.shift(1))
    lx = (c < basis) & (c.shift(1) >= basis.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
