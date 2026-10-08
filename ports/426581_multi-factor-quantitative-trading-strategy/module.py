"""EMA ribbon + RSI + stochastic from flat: with EMAs 8 > 13 > 21 > 34 > 55, RSI(14) between 40 and
70 and %K under 80, go long; leave when EMA 13 < EMA 55, RSI > 70 or %K > 95 (shorts mirrored).
Port of FMZ strategy #426581 "Multi factor Quantitative Trading Strategy".

Source
    https://www.fmz.com/strategy/426581 (PineScript v4, FMZ last modified 2023-09-13 14:46:59).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 121-178), EMA 8 / 13 / 21 / 34 / 55, RSI 14, stoch 14
    long  = ribbon up and 40 < rsi < 70 and k < 80 and flat;  exit long: ema13 < ema55 or rsi > 70 or k > 95
    short = ribbon down and 30 < rsi < 60 and k > 20 and flat; exit short: ema13 > ema55 or rsi < 30 or k < 5

Interpretation choices (Pine rules in SURVEY_README.md)
    * Same rules as #426561 with the 8..55 ribbon (near-duplicate, possible_duplicates 0.69).
    * Entries only from flat, exits only while in position (both tested on the position held at
      the bar close). Opposite entries cannot occur.
    * FREQ = "2D" from the backtest header (period 2d). Two-day bars are built from broker days
      (session ending 17:00 New York), in fixed blocks of two broker-day dates counted from
      1970-01-01 (block phase: decision owed), stamped with the first session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426581_ema_ribbon_rsi_stoch_flat"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
BLOCK_DAYS = 2

GRID = {
    "emas": [(8, 13, 21, 34, 55), (5, 9, 13, 21, 34)],
}
DEFAULT_PARAMS = {"emas": (8, 13, 21, 34, 55)}


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


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi_pine(close, n):
    """rsi() as Pine defines it: 100 when the average loss is 0, 0 when the average gain is 0."""
    d = close.diff()
    up, down = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    rsi = 100.0 - 100.0 / (1.0 + up / down)
    return rsi.mask(up == 0, 0.0).mask(down == 0, 100.0).where(up.notna() & down.notna())


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
    return _multiday(raw_1m_df, days=BLOCK_DAYS)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e = [c.ewm(span=int(n), adjust=False).mean() for n in p["emas"]]
    rsi = _rsi_pine(c, 14)
    lo, hi = l.rolling(14).min(), h.rolling(14).max()
    k = 100 * (c - lo) / (hi - lo)
    long_c = ((e[0] > e[1]) & (e[1] > e[2]) & (e[2] > e[3]) & (e[3] > e[4])
              & (rsi < 70) & (rsi > 40) & (k < 80)).to_numpy()
    short_c = ((e[0] < e[1]) & (e[1] < e[2]) & (e[2] < e[3]) & (e[3] < e[4])
               & (rsi > 30) & (rsi < 60) & (k > 20)).to_numpy()
    x_long = ((e[1] < e[4]) | (rsi > 70) | (k > 95)).to_numpy()
    x_short = ((e[1] > e[4]) | (rsi < 30) | (k < 5)).to_numpy()
    target = np.zeros(len(c), dtype=int)
    pos = 0
    for i in range(len(c)):
        before = pos
        if before == 0 and long_c[i]:
            pos = 1
        elif before == 1 and x_long[i]:
            pos = 0
        if before == 0 and short_c[i]:
            pos = -1
        elif before == -1 and x_short[i]:
            pos = 0
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
