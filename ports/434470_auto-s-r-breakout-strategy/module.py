"""Pivot support / resistance crosses, broker days: support is the low of the last confirmed close pivot low (50 bars left,
5 right) and resistance the high of the last close pivot high; a close crossing above support goes long, a close crossing
below resistance goes short; held otherwise and reversed on the opposite cross.
Port of FMZ strategy #434470 "Auto S R Breakout Strategy" (Auto S/R Strategy).

FMZ source id: 434470

Source
    https://www.fmz.com/strategy/434470 (PineScript v5, FMZ last modified 2023-12-06 16:51:30).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 119-142), left 50, right 25 (unused), quick right 5; source close
    res = valuewhen(pivothigh(close, 50, 5), high[5], 0);  sup = valuewhen(pivotlow(close, 50, 5), low[5], 0)
    crossover(close, sup) -> entry long;  crossunder(close, res) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A pivot is confirmed at bar t when the close 5 bars back is strictly above (below) the 50
      closes before it and the 5 after it (only past bars read); its level is that bar's high
      (low). The 25-bar pivots are computed but unused: dropped.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price against its own pivot levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_434470_pivot_sr_cross"
FAMILY = "pivot_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "left": [50, 20],
    "right": [5, 3],
}
DEFAULT_PARAMS = {"left": 50, "right": 5}


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


def _pivots(x, lb, rb, high):
    """True at bar t when bar t - rb is a strict pivot over lb bars before and rb bars after."""
    m = len(x)
    out = np.zeros(m, dtype=bool)
    for t in range(lb + rb, m):
        j = t - rb
        v = x[j]
        left, right = x[j - lb:j], x[j + 1:t + 1]
        if high:
            out[t] = v > left.max() and v > right.max()
        else:
            out[t] = v < left.min() and v < right.min()
    return out


def _vw0(cond, x):
    """valuewhen(cond, x, 0): x at the most recent bar where cond held (this bar included)."""
    out = np.full(len(x), np.nan)
    last = np.nan
    for t in range(len(x)):
        if cond[t]:
            last = x[t]
        out[t] = last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    lb, rb = int(p["left"]), int(p["right"])
    cv = c.to_numpy(dtype=float)
    res = _vw0(_pivots(cv, lb, rb, True), h.shift(rb).to_numpy(dtype=float))
    sup = _vw0(_pivots(cv, lb, rb, False), lo.shift(rb).to_numpy(dtype=float))
    c1 = np.concatenate(([np.nan], cv[:-1]))
    r1 = np.concatenate(([np.nan], res[:-1]))
    s1 = np.concatenate(([np.nan], sup[:-1]))
    with np.errstate(invalid="ignore"):
        lc = (cv > sup) & (c1 <= s1)
        sc = (cv < res) & (c1 >= r1)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if lc[i]:
            q = 1
        if sc[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
