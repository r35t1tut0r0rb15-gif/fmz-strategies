"""T3 channel (always in): with the T3(24) of the close rising and OHLC4 above T3 + T3(range), the
direction turns long; with T3 falling and OHLC4 below T3 - T3(range), short; each turn enters.
Port of FMZ strategy #426786 "T3 Moving Average Channel Breakout Strategy".

Source
    https://www.fmz.com/strategy/426786 (PineScript v4, FMZ last modified 2023-09-14 15:51:25).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 125-178), length 24, b 0.7
    t3(x, n) = c1 e6 + c2 e5 + c3 e4 + c4 e3 (e1..e6 nested ema(n); b = 0.7)
    upper / lower = t3(close) +- t3(high - low)
    buy = t3 rising and ohlc4 > upper;  sell = t3 falling and ohlc4 < lower
    direction = buy ? 1 : sell ? -1 : direction[1];  a change to 1 -> entry long, to -1 -> short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4D" from the backtest header (period 4d). Four-day bars are built from broker days
      (session ending 17:00 New York), in fixed blocks of four broker-day dates counted from
      1970-01-01 (block phase: decision owed), stamped with the first session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426786_t3_channel"
FAMILY = "ma_envelope_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "4D"  # backtest header period: 4d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [12, 24, 36],
}
DEFAULT_PARAMS = {"length": 24, "b": 0.7}


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


def _t3(x, n, b):
    e = [x]
    for _ in range(6):
        e.append(e[-1].ewm(span=n, adjust=False).mean())
    c1 = -b ** 3
    c2 = 3 * b * b + 3 * b ** 3
    c3 = -6 * b * b - 3 * b - 3 * b ** 3
    c4 = 1 + 3 * b + b ** 3 + 3 * b * b
    return c1 * e[6] + c2 * e[5] + c3 * e[4] + c4 * e[3]


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=4)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n, b = int(p["length"]), p["b"]
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    t3 = _t3(c, n, b)
    rng = _t3(h - l, n, b)
    ohlc4 = (o + h + l + c) / 4
    buy = ((t3 > t3.shift(1)) & (ohlc4 > t3 + rng)).to_numpy()
    sell = ((t3 < t3.shift(1)) & (ohlc4 < t3 - rng)).to_numpy()
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
