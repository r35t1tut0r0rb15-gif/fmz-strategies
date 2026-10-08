"""Noro's bands scalper: a price-channel trend (close beyond the centre +- its average distance)
sets the side. In an up-trend two red bars go long and two green bars closing above the entry
price close the long; in a down-trend two green bars go short and two red bars closing below
the entry price close the short.
Port of FMZ strategy #426995 "Dynamic Price Channel Trading Strategy".

Source
    https://www.fmz.com/strategy/426995 (PineScript v2/v3 syntax, FMZ last modified 2023-09-16 19:01:26).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 145-193), period 20, take 0 %, counter-trend off
    center = (highest(close, 20) + lowest(close, 20)) / 2; dsma = sma(|close - center|, 20)
    trend = close < center - dsma and high < center + dsma ? -1
          : close > center + dsma and low > center - dsma ? 1 : trend[1]
    up7 = trend 1, two red bars -> entry long
    dn7 = trend 1, two green bars, close > avg price -> entry short with qty 0 (closes a long)
    up8 = trend -1, two red bars, close < avg price -> entry long with qty 0 (closes a short)
    dn8 = trend -1, two green bars -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Counter-trend entries are off, so an entry against the trend has qty 0: it only closes the
      opposite position (Noro's idiom). The average price is the position's fill (the next
      open after the signal); with no position it is na and the closing tests are false.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "2D" from the backtest header (period 2d). Two-day bars are built from broker days
      (session ending 17:00 New York), in fixed blocks of two broker-day dates counted from
      1970-01-01 (block phase: decision owed), stamped with the first session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426995_noro_bands_scalper"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20, 40],
}
DEFAULT_PARAMS = {"length": 20, "takepercent": 0.0}


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
    return _multiday(raw_1m_df, days=2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    center = (c.rolling(n).max() + c.rolling(n).min()) / 2
    dsma = (c - center).abs().rolling(n).mean()
    hd, ld = center + dsma, center - dsma
    t_dn = ((c < ld) & (h < hd)).to_numpy()
    t_up = ((c > hd) & (l > ld)).to_numpy()
    bar = np.sign(c - o)
    two_red = ((bar == -1) & (bar.shift(1) == -1)).to_numpy()
    two_green = ((bar == 1) & (bar.shift(1) == 1)).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tk = p["takepercent"]
    m = len(cv)
    target = np.zeros(m, dtype=int)
    trend = 0
    entry = np.nan
    for i in range(m):
        if i > 0 and target[i - 1] != (target[i - 2] if i > 1 else 0):
            entry = ov[i] if target[i - 1] != 0 else np.nan
        trend = -1 if t_dn[i] else (1 if t_up[i] else trend)
        before = target[i - 1] if i > 0 else 0
        pos = before
        if trend == 1 and two_red[i]:
            pos = 1                                              # up7
        elif trend == -1 and two_red[i] and cv[i] < entry * (100 - tk) / 100 and before == -1:
            pos = 0                                              # up8 (qty 0): closes the short
        if trend == 1 and two_green[i] and cv[i] > entry * (100 + tk) / 100 and before == 1:
            pos = 0                                              # dn7 (qty 0): closes the long
        elif trend == -1 and two_green[i]:
            pos = -1                                             # dn8
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
