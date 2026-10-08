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
    * Same bar: from flat an entry stands (the close finds no position); while long the entry
      is refused and the close goes flat.

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


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    fast = c.ewm(span=int(p["fast"]), adjust=False).mean()
    slow = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (fast > slow) & (fast.shift(1) <= slow.shift(1))
    lx = (c < fast) & (c.shift(1) >= fast.shift(1))
    entry, out = le.to_numpy(), lx.to_numpy()
    target = np.zeros(len(entry), dtype=int)
    pos = 0
    for i in range(len(entry)):  # Pine order: entry, then close of the position held at the close
        if pos == 0 and entry[i]:
            pos = 1
        elif pos == 1 and out[i]:
            pos = 0
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
