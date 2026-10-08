"""OHLC4 momentum, long only: five rising OHLC4 values in a row (each above the one before) go
long; four falling in a row close the long.
Port of FMZ strategy #426502 "Momentum Moving Average Persistent Long Trading Strategy".

Source
    https://www.fmz.com/strategy/426502 (PineScript v4, FMZ last modified 2023-09-12 16:15:44).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 109-124)
    candela = ohlc4
    candela > candela[1] > ... > candela[5]  -> entry long
    candela < candela[1] < ... < candela[4]  -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only (no short entry). The risk input does not reach the orders.
    * FREQ = "3D" from the backtest header (period 3d). Three-day bars are built from broker
      days (session ending 17:00 New York), in fixed blocks of three broker-day dates counted
      from 1970-01-01 (the block phase is a port choice; decision owed). Each bar is stamped with
      the session start of its first broker day.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426502_ohlc4_momentum_long"
FAMILY = "momentum_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "3D"  # backtest header period: 3d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "up_bars": [3, 5],
    "down_bars": [3, 4],
}
DEFAULT_PARAMS = {"up_bars": 5, "down_bars": 4}


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


def _multiday(raw_1m_df, weekly=False, days=1):
    """Multi-day bars built from broker days: calendar weeks (Monday-Sunday) of the broker-day
    dates when weekly, else blocks of `days` broker-day dates counted from 1970-01-01. Each bar
    is stamped with the session start of its first broker day."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    if weekly:
        key = np.asarray(day - pd.to_timedelta(day.weekday, unit="D"))
    else:
        key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def _run(cond, n):
    """cond held on this bar and the n - 1 before it."""
    return cond.astype(float).rolling(n).sum() == n


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=3)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    x = (bars_df["open"] + bars_df["high"] + bars_df["low"] + bars_df["close"]) / 4
    le = _run(x > x.shift(1), int(p["up_bars"]))
    lx = _run(x < x.shift(1), int(p["down_bars"]))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
