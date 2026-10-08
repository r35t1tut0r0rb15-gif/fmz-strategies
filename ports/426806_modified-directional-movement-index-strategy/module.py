"""Modified DMI (always in): DI+ minus DI- built from the changes of the 9-bar highest high and
lowest low, smoothed by EMA 9; above 0 and rising goes long, below 0 and falling goes short.
Port of FMZ strategy #426806 "Modified Directional Movement Index Strategy".

Source
    https://www.fmz.com/strategy/426806 (PineScript v4, FMZ last modified 2023-09-14 16:41:00).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 157-232), length 9, smoothing EMA 9
    up = change(highest(high, 9)); down = -change(lowest(low, 9)); trur = rma(tr, 9)
    plus = fixnan(100 rma(up > down and up > 0 ? up : 0, 9) / trur); minus mirrors
    result = ema(plus - minus, 9)
    result > 0 and result > result[1] -> close short, entry long
    result < 0 and result < result[1] -> close long, entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Without an na guard, the first bar's na change counts as 0 directional movement.
    * Shorts allowed (source default). strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "3D" from the backtest header (period 3d). Three-day bars are built from broker
      days (session ending 17:00 New York), in fixed blocks of three broker-day dates counted
      from 1970-01-01 (block phase: decision owed), stamped with the first session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426806_modified_dmi"
FAMILY = "directional_movement"  # proposed 2026-10-07, user to confirm
FREQ = "3D"  # backtest header period: 3d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [9, 14],
    "smoothing": [5, 9],
}
DEFAULT_PARAMS = {"length": 9, "smoothing": 9}


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


def _fixnan(v):
    """Pine fixnan: replace na by the last non-na value (past values only)."""
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1]
    return out


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=3)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up = h.rolling(n).max().diff()
    down = -l.rolling(n).min().diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=h.index)
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=h.index)
    pc = c.shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    trur = _rma(tr, n)
    plus = _fixnan((100 * _rma(plus_dm, n) / trur).to_numpy())
    minus = _fixnan((100 * _rma(minus_dm, n) / trur).to_numpy())
    res = pd.Series(plus - minus, index=h.index).ewm(span=int(p["smoothing"]), adjust=False).mean()
    r1 = res.shift(1)
    long_ = ((res > 0) & (res > r1)).to_numpy()
    short = ((res < 0) & (res < r1)).to_numpy()
    return _always_in(long_, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
