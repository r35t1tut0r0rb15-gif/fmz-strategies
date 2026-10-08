"""EMA 13 / 48 cross, long only: EMA 13 crossing above EMA 48 goes long; the close crossing under
EMA 13 closes the long.
Port of FMZ strategy #426521 "Fast and Slow EMA Crossover Trend Trading Strategy".

Source
    https://www.fmz.com/strategy/426521 (PineScript v2/v3 syntax, FMZ last modified 2023-09-12 18:06:26).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 108-126), EMA 13 / 48
    crossover(ema13, ema48) -> entry long;  crossunder(close, ema13) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only: the short orders are commented out in the source.
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426521_ema_13_48_long"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 13, 21],
    "slow": [48, 100],
}
DEFAULT_PARAMS = {"fast": 13, "slow": 48}


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
    c = bars_df["close"]
    fast = c.ewm(span=int(p["fast"]), adjust=False).mean()
    slow = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (fast > slow) & (fast.shift(1) <= slow.shift(1))
    lx = (c < fast) & (c.shift(1) >= fast.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
