"""SuperTrend flips entered one bar late, 3-day bars: a flip to up goes long on the bar after the flip, a
flip to down goes short on the bar after it.
Port of FMZ strategy #428703 "SuperTrend Dual Direction Strategy".

FMZ source id: 428703

Source
    https://www.fmz.com/strategy/428703 (PineScript v4, FMZ last modified 2023-10-08 15:02:45).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 165-202), ATR 10 (Wilder), multiplier 3, source hl2
    up = hl2 - 3 atr, ratcheted up while close[1] > up[1]; dn = hl2 + 3 atr, ratcheted down while close[1] < dn[1]
    trend flips to 1 when close > dn[1], to -1 when close < up[1]
    buySignal[1] -> entry long; sellSignal[1] -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Change ATR Calculation Method" defaults to true: Wilder atr(10).
    * The strategy() line (process_orders_on_close, calc_on_every_tick, cash sizing) is commented
      out, so the defaults apply: bar-close evaluation, orders at the next open. The date window is
      dropped (time_cond is true).
    * The signals are read one bar late (`buySignal[1]`), as written.
    * strategy.entry reverses: REVERSAL INTENDED.
    * Multi-day bars are blocks of 3 broker days (17:00 America/New_York) counted from 1970-01-01,
      each stamped with its first minute. FREQ = "3D" from the backtest header (period 3d).

Admission criteria
    1 fits the interface: PASS, bar-close orders (the intrabar settings are in a commented-out line).
    2 generic: PASS, an ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital / position / commission constants and the commented-out strategy() stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428703_supertrend_late_flip"
FAMILY = "supertrend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3D"  # backtest header period: 3d (blocks of 3 broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "periods": [10, 14],
    "multiplier": [3.0, 2.0],
}
DEFAULT_PARAMS = {"periods": 10, "multiplier": 3.0, "days": 3}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, int(p["periods"])).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy()
    m = len(cv)
    up, dn = np.full(m, np.nan), np.full(m, np.nan)
    trend = np.ones(m, dtype=np.int8)
    for i in range(m):
        ur = src[i] - p["multiplier"] * atr[i]
        dr = src[i] + p["multiplier"] * atr[i]
        u1 = up[i - 1] if i >= 1 and not np.isnan(up[i - 1]) else ur
        d1 = dn[i - 1] if i >= 1 and not np.isnan(dn[i - 1]) else dr
        up[i] = max(ur, u1) if i >= 1 and cv[i - 1] > u1 else ur
        dn[i] = min(dr, d1) if i >= 1 and cv[i - 1] < d1 else dr
        t = trend[i - 1] if i >= 1 else 1
        if t == -1 and cv[i] > d1:
            t = 1
        elif t == 1 and cv[i] < u1:
            t = -1
        trend[i] = t
    prev = np.concatenate(([1], trend[:-1]))
    buy = (trend == 1) & (prev == -1)
    sell = (trend == -1) & (prev == 1)
    idx = bars_df.index
    long_e = pd.Series(np.concatenate(([False], buy[:-1])), index=idx)
    short_e = pd.Series(np.concatenate(([False], sell[:-1])), index=idx)
    false = pd.Series(False, index=idx)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
