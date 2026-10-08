"""Bollinger cross reversion ("Pair Trade L/S", single instrument): the close crossing the lower
band (either way) goes long, crossing the upper band goes short, and crossing the 20-bar mean
closes the position.
Port of FMZ strategy #426262 "Pair trading strategy".

Source
    https://www.fmz.com/strategy/426262 (PineScript v4, FMZ last modified 2023-09-10 00:17:24).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 77-101), SMA 20, entry z 2.0
    ma = sma(close, 20); upper / lower = ma +- 2 * stdev(close, 20)
    cross(close, lower) -> entry long;  cross(close, upper) -> entry short
    cross(close, ma) -> strategy.close_all(immediately = true)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.cross is either direction, as written. stdev is Pine's population deviation.
    * close_all(immediately = true) fills at the signal bar's close; the contract fills at the
      next open (the same price on a 24 h market up to the gap). Entries placed on the same bar
      fill at the next open after it, so the bar leaves the entry's side (short after long when
      both fire); an exit plus a same-side entry nets to holding.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * The start-year filter (2016) is a backtest window: dropped.
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426262_bollinger_cross_reversion"
FAMILY = "bollinger_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 30],
    "zscore": [1.5, 2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "zscore": 2.0}


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


def _emit(target, index):
    """Signals from the position each bar's orders leave (1 / 0 / -1): a change to +-1 is an
    entry (reversing an opposite position), a change to 0 an exit of the side held."""
    m = len(target)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    prev = 0
    for i in range(m):
        n = target[i]
        if n != prev:
            if n == 1:
                le[i] = True
            elif n == -1:
                se[i] = True
            elif prev == 1:
                lx[i] = True
            else:
                sx[i] = True
        prev = n
    return tuple(pd.Series(x, index=index) for x in (le, lx, se, sx))


def _cross(a, b):
    """Pine cross(): a crossed b in either direction on this bar."""
    d, d1 = a - b, (a - b).shift(1)
    return ((d > 0) & (d1 <= 0)) | ((d < 0) & (d1 >= 0))


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    c = bars_df["close"]
    ma = c.rolling(n).mean()
    dev = p["zscore"] * c.rolling(n).std(ddof=0)
    long_ = _cross(c, ma - dev).to_numpy()
    short = _cross(c, ma + dev).to_numpy()
    flat = _cross(c, ma).to_numpy()
    target = np.zeros(len(c), dtype=int)
    pos = 0
    for i in range(len(c)):
        if short[i]:
            pos = -1
        elif long_[i]:
            pos = 1
        elif flat[i]:
            pos = 0
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
