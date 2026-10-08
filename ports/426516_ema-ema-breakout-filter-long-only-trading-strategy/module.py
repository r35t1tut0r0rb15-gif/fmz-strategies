"""EMA +- ATR breakout, long only (weekly): SMA 2 of the close crossing above EMA 21 + ATR 21 goes
long; crossing under EMA 21 - ATR 21 closes the long.
Port of FMZ strategy #426516 "EMA Breakout Filter Long Only Trading Strategy".

Source
    https://www.fmz.com/strategy/426516 (PineScript v2/v3 syntax, FMZ last modified 2023-09-12 17:12:22).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 105-116), length 21
    price = sma(close, 2); average = ema(close, 21); diff = atr(21)
    crossover(price, average + diff) -> entry long;  crossover(average - diff, price) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only (the short entry is commented out).
    * FREQ = "1W" from the backtest header (period 7d). Weekly bars are built from broker days
      (session ending 17:00 New York), one bar per calendar week (Monday-Sunday) of the
      broker-day dates, stamped with the session start of its first broker day.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426516_ema_atr_breakout_long"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "1W"  # backtest header period: 7d (weeks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 21, 30],
}
DEFAULT_PARAMS = {"length": 21}


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


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, weekly=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    c = bars_df["close"]
    price = c.rolling(2).mean()
    avg = c.ewm(span=n, adjust=False).mean()
    atr = _atr_pine(bars_df, n)
    bull, bear = avg + atr, avg - atr
    le = (price > bull) & (price.shift(1) <= bull.shift(1))
    lx = (bear > price) & (bear.shift(1) <= price.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
