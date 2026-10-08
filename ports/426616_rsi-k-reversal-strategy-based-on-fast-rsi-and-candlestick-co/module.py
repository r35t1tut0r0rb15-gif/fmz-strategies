"""Noro's Hundred: four red bars in a row with the fast RSI(7) under 30 go long (from flat or
long); four green bars with it over 70 go short (from flat or short). A long is closed on a green
bar closing above the entry price, a short on a red bar closing below it.
Port of FMZ strategy #426616 "RSI K Reversal Strategy Based on Fast RSI and Candlestick Colors".

Source
    https://www.fmz.com/strategy/426616 (PineScript v2/v3 syntax, FMZ last modified 2023-09-13 17:24:54).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 99-154), fast RSI 7, limit 30, RSI bars 1, colour bars 4
    fastrsi = Noro's RSI (rma 7; 100 if down == 0, 0 if up == 0)
    bar = sign(close - open);  up = sma(bar, 4) == -1 and position >= 0 and fastrsi < 30
    dn = sma(bar, 4) == 1 and position <= 0 and fastrsi > 70
    exit = ((position > 0 and bar == 1) or (position < 0 and bar == -1)) and profit
    profit = (long and close > avg price) or (short and close < avg price)   (onlyprofit on)
    up -> entry long;  dn -> entry short;  exit -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry price is the fill: the open of the bar after the signal. simulate() tracks it
      (pyramiding 0: one position). up needs no short and dn no long, so a position never
      reverses; it ends only by exit. Opposite entries cannot occur.
    * The leverage lot is sizing (original_sizing.txt). The date window is dropped.
    * FREQ = "4D" from the backtest header (period 4d). Four-day bars are built from broker days
      (session ending 17:00 New York), in fixed blocks of four broker-day dates counted from
      1970-01-01 (block phase: decision owed), stamped with the first session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426616_noro_hundred"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "4D"  # backtest header period: 4d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 7],
    "limit": [20, 30],
    "cbars": [3, 4],
}
DEFAULT_PARAMS = {"fast": 7, "limit": 30, "cbars": 4, "only_profit": True}


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
    return _multiday(raw_1m_df, days=4)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    rsi = _rsi_pine(c, int(p["fast"])).to_numpy()
    bar = np.sign(c - o)
    run = bar.rolling(int(p["cbars"])).mean().to_numpy()
    ov, cv, bv = o.to_numpy(dtype=float), c.to_numpy(dtype=float), bar.to_numpy()
    m = len(cv)
    target = np.zeros(m, dtype=int)
    pos, pending, entry = 0, 0, np.nan
    for i in range(m):
        if pending:
            pos, entry, pending = pending, ov[i], 0
        up = run[i] == -1 and pos >= 0 and rsi[i] < p["limit"]
        dn = run[i] == 1 and pos <= 0 and rsi[i] > 100 - p["limit"]
        profit = (pos > 0 and cv[i] > entry) or (pos < 0 and cv[i] < entry) or not p["only_profit"]
        ex = ((pos > 0 and bv[i] == 1) or (pos < 0 and bv[i] == -1)) and profit
        new = pos
        if up and pos == 0:
            new = 1
        elif dn and pos == 0:
            new = -1
        if ex:
            new = 0
        if new != pos:
            if new == 0:
                pos, entry = 0, np.nan
            else:
                pending = new
        target[i] = new
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
