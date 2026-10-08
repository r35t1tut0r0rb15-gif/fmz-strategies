"""Pivot breakout, long only: a close above the last confirmed 10 / 10 pivot high goes long; a
close below the last confirmed pivot low closes the long.
Port of FMZ strategy #426613 "Trend Following Strategy Based on Pivot Point Breakout".

Source
    https://www.fmz.com/strategy/426613 (PineScript v4, FMZ last modified 2023-09-13 17:20:40).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 81-94), left 10, right 10
    pivot_high = nz(pivothigh(high, 10, 10), pivot_high[1]);  pivot_low likewise
    close > pivot_high[1] -> entry long;  close < pivot_low[1] -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * A pivot is known 10 bars after its centre (confirmation bar), as Pine. Until the first
      pivot the level is na and nothing trades.
    * Long only (no short entry).
    * FREQ = "3D" from the backtest header (period 3d). Three-day bars are built from broker
      days (session ending 17:00 New York), in fixed blocks of three broker-day dates counted
      from 1970-01-01 (block phase: decision owed), stamped with the first session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426613_pivot_breakout_long"
FAMILY = "pivot_reversal"  # proposed 2026-10-07, user to confirm
FREQ = "3D"  # backtest header period: 3d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "left": [5, 10],
    "right": [5, 10],
}
DEFAULT_PARAMS = {"left": 10, "right": 10}


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


def _pivots(x, left, right, high):
    """ta.pivothigh/pivotlow(x, left, right): value of the pivot confirmed on each bar (NaN if
    none); the centre bar t-right strictly beyond the `left` bars before and `right` bars after."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    for t in range(left + right, len(v)):
        c = t - right
        side = np.concatenate([v[c - left:c], v[c + 1:t + 1]])
        if np.isnan(v[c]) or np.isnan(side).any():
            continue
        if (high and v[c] > side.max()) or (not high and v[c] < side.min()):
            out[t] = v[c]
    return out


def _last(v):
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1]
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=3)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lt, rt = int(p["left"]), int(p["right"])
    idx = bars_df.index
    ph = pd.Series(_last(_pivots(bars_df["high"], lt, rt, True)), index=idx)
    pl = pd.Series(_last(_pivots(bars_df["low"], lt, rt, False)), index=idx)
    c = bars_df["close"]
    le = c > ph.shift(1)
    lx = c < pl.shift(1)
    false = pd.Series(False, index=idx)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
