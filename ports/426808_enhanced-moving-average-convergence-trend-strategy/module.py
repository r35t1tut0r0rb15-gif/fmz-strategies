"""MACD-of-histogram, long only: the MACD histogram crossing above its own EMA 9 goes long;
crossing under closes the long.
Port of FMZ strategy #426808 "Enhanced Moving Average Convergence Trend Strategy".

Source
    https://www.fmz.com/strategy/426808 (PineScript v2/v3 syntax, FMZ last modified 2023-09-14 16:46:53).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 151-165), 12 / 26 / 9
    hist = macd - ema(macd, 9);  sig = ema(hist, 9)
    crossover(hist, sig) -> entry long;  crossunder(hist, sig) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * inTimeRange is hard-coded true. Long only (no short entry).
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426808_macd_of_histogram_long"
FAMILY = "macd_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 12],
    "slow": [26, 34],
    "signal": [9, 5],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


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
    ema = lambda x, n: x.ewm(span=int(n), adjust=False).mean()
    macd = ema(c, p["fast"]) - ema(c, p["slow"])
    hist = macd - ema(macd, p["signal"])
    d = hist - ema(hist, p["signal"])
    d1 = d.shift(1)
    le = (d > 0) & (d1 <= 0)
    lx = (d < 0) & (d1 >= 0)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
