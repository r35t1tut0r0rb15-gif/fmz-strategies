"""TEMA 5 / 8 cross, long only: the fast TEMA of hlc3 crossing above the slow one, with the close
above the close 2 bars ago, goes long; crossing below closes the long.
Port of FMZ strategy #426510 "TEMA Crossover Trading Strategy".

Source
    https://www.fmz.com/strategy/426510 (PineScript v4, FMZ last modified 2023-09-12 16:40:50).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 118-148), TEMA 5 / 8, direction bars 2
    tema(x, n) = 3 e1 - 3 e2 + e3 (e1 = ema(x, n), e2 = ema(e1, n), e3 = ema(e2, n))
    crossover(tema(hlc3, 5), tema(hlc3, 8)) and close / close[2] > 1 -> entry long
    crossunder(...) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only (no short entry). The test period (2017-9999) is a backtest window: dropped.
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426510_tema_cross_long"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [3, 5],
    "slow": [8, 13],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 8, "dir_bars": 2}


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


def _tema(x, n):
    e1 = x.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    e3 = e2.ewm(span=n, adjust=False).mean()
    return 3 * e1 - 3 * e2 + e3


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    hlc3 = (bars_df["high"] + bars_df["low"] + c) / 3
    d = _tema(hlc3, int(p["fast"])) - _tema(hlc3, int(p["slow"]))
    d1 = d.shift(1)
    up_dir = c / c.shift(int(p["dir_bars"])) > 1
    le = (d > 0) & (d1 <= 0) & up_dir
    lx = (d < 0) & (d1 >= 0)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
