"""ATR renko on closes vs opens, broker days, long only: a close-brick and an open-brick series each
step one ATR(10) per bar toward price; when the close brick rises above the previous open brick (after
having been below) the colour turns green and the strategy goes long; it closes when it turns red.
Port of FMZ strategy #427998 "Renko Yin Yang Quant Trading Strategy" (Renko Strategy V2).

FMZ source id: 427998

Source
    https://www.fmz.com/strategy/427998 (PineScript v4, FMZ last modified 2023-09-27 17:11:30).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 139-233), ATR 10, shorts off
    c2 = Renko1: p := close > p[1] + atr ? p[1] + atr : close < p[1] - atr ? p[1] - atr : p[1] (from 0)
    o2 = Renko4: the previous Renko3 value (the same on opens) whenever Renko3 changes, else held
    go_long = barssince(o2 < c2) < barssince(o2 > c2) and o2 < c2; go_short mirrors
    colour green / red / white; long on a change to green; close the long on red

Interpretation choices (Pine rules in SURVEY_README.md)
    * AS WRITTEN: the bricks start at 0 (nz) and move at most one ATR per bar, so they climb from 0
      toward the price over the first bars (no orders until the colours form).
    * barssince is na before the first event (Pine): go_long needs both events seen. Renko2 is unused.
    * Shorts are off by default: Long only. The date window is dropped.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR bricks only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: cash quantity 10000 stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427998_renko_close_open_bricks_long"
FAMILY = "renko_bricks"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_len": [10, 5, 14, 20],
}
DEFAULT_PARAMS = {"atr_len": 10}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
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


def _bricks(x, atr):
    out = np.zeros(len(x))
    p = 0.0
    for i in range(len(x)):
        a = atr[i]
        if not np.isnan(a):
            if x[i] > p + a:
                p = p + a
            elif x[i] < p - a:
                p = p - a
        out[i] = p
    return out


def _barssince(cond):
    out = np.full(len(cond), np.nan)
    last = -1
    for i, v in enumerate(cond):
        if v:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, o = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["open"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_len"])).to_numpy()
    c2 = _bricks(c.to_numpy(dtype=float), atr)
    p3 = _bricks(o.to_numpy(dtype=float), atr)
    m = len(c2)
    o2 = np.zeros(m)
    ov = 0.0
    for i in range(1, m):
        if p3[i] != p3[i - 1]:
            ov = p3[i - 1]
        o2[i] = ov
    up, dn = o2 < c2, o2 > c2
    bu, bd = _barssince(up), _barssince(dn)
    with np.errstate(invalid="ignore"):
        go_long = (bu < bd) & up
        go_short = (bu > bd) & dn
    colour = np.where(go_long, 1, np.where(go_short, -1, 0))
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(1, m):
        changed = colour[i] != colour[i - 1]
        if colour[i] == 1 and changed:
            pos = 1
        elif colour[i] == -1:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
