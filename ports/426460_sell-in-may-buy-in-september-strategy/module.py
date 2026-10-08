"""Sell in May, buy in September, long only: any daily bar in September goes long (from flat), any
bar in May closes the long.
Port of FMZ strategy #426460 "Sell in May Buy in September Strategy".

Source
    https://www.fmz.com/strategy/426460 (PineScript v5, FMZ last modified 2023-09-12 11:18:34).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 65-74)
    month == 9 -> entry long;  month == 5 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only (no short entry). The month of a bar is the month of its broker day (the session
      ending 17:00 New York that the bar is).
    * Daily bars are broker days, stamped with the session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426460_sell_may_buy_september"
FAMILY = "calendar_seasonal"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "buy_month": [9, 10, 11],
    "sell_month": [5],
}
DEFAULT_PARAMS = {"buy_month": 9, "sell_month": 5}


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
    month = pd.Series(broker_day(bars_df.index).month, index=bars_df.index)
    le = month == int(p["buy_month"])
    lx = month == int(p["sell_month"])
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
