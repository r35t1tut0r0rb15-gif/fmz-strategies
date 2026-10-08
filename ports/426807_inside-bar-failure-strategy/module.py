"""Inside-bar failure: after an inside bar, a bar breaking below it but closing back above its low
goes long; one breaking above it but closing back below its high goes short. Each position is
closed 3 bars after its signal.
Port of FMZ strategy #426807 "Inside Bar Failure Strategy".

Source
    https://www.fmz.com/strategy/426807 (PineScript v4, FMZ last modified 2023-09-14 16:43:52).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 116-131), look forward 3
    inside = high[2] > high[1] and low[2] < low[1]
    long  = inside and low < low[1] and high < high[1] and close > low[1]
    short = inside and high > high[1] and low > low[1] and close < high[1]
    long -> entry long; short -> entry short; long[3] -> close long; short[3] -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Orders fill at the next open in issue order: an entry reversing the other side stands
      (that side's timed close then finds nothing); a same-side signal while held is refused, and
      a timed close of that side on the same bar goes flat.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4D" from the backtest header (period 4d). Four-day bars are built from broker days
      (session ending 17:00 New York), in fixed blocks of four broker-day dates counted from
      1970-01-01 (block phase: decision owed), stamped with the first session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426807_inside_bar_failure"
FAMILY = "candle_pattern"  # proposed 2026-10-07, user to confirm
FREQ = "4D"  # backtest header period: 4d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "forward": [2, 3, 5],
}
DEFAULT_PARAMS = {"forward": 3}


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
    return _multiday(raw_1m_df, days=4)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    h1, l1, h2, l2 = h.shift(1), l.shift(1), h.shift(2), l.shift(2)
    inside = (h2 > h1) & (l2 < l1)
    lc = inside & (l < l1) & (h < h1) & (c > l1)
    sc = inside & (h > h1) & (l > l1) & (c < h1)
    k = int(p["forward"])
    lcv, scv = lc.to_numpy(), sc.to_numpy()
    lck = lc.shift(k, fill_value=False).to_numpy()
    sck = sc.shift(k, fill_value=False).to_numpy()
    target = np.zeros(len(c), dtype=int)
    pos = 0
    for i in range(len(c)):
        before = pos
        new = -1 if scv[i] else (1 if lcv[i] else before)
        if new == before == 1 and lck[i]:
            new = 0
        elif new == before == -1 and sck[i]:
            new = 0
        pos = new
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
