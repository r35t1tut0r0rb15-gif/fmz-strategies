"""Simple momentum, broker days: a close above each of the previous 2 closes goes long, below each of them
goes short; a close below the previous close exits a long, above it exits a short.
Port of FMZ strategy #428785 "Dual Momentum Strategy" (simple momentum).

FMZ source id: 428785

Source
    https://www.fmz.com/strategy/428785 (PineScript v4, FMZ last modified 2023-10-09 15:03:30).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 204-227), enter after 2 rising / falling blocks, exit after 1
    LongEnter = rising(close, 2); LongExit = falling(close, 1)
    ShortEnter = falling(close, 2); ShortExit = rising(close, 1)
    entry long / close long / entry short / close short, in that order

Interpretation choices (Pine rules in SURVEY_README.md)
    * rising(x, n) = x above each of the n previous values; falling the mirror. change(time) is
      true on every bar after the first.
    * A short entry while long (falling 2 implies the long's exit) reverses in one bar: REVERSAL
      INTENDED. The year / month filter (from 2017-01) is the author's backtest window: dropped.
    * The strategy() line is commented out; the defaults apply.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close comparisons only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out strategy() line stored.
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

NAME = "fmz_428785_simple_momentum_blocks"
FAMILY = "momentum_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "enter_after": [2, 3],
    "exit_after": [1, 2],
}
DEFAULT_PARAMS = {"enter_after": 2, "exit_after": 1}


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


def _rising(c, n):
    return (c > c.shift(1).rolling(n).max()).to_numpy()


def _falling(c, n):
    return (c < c.shift(1).rolling(n).min()).to_numpy()


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ne, nx = int(p["enter_after"]), int(p["exit_after"])
    le_c, se_c = _rising(c, ne), _falling(c, ne)
    lx_c, sx_c = _falling(c, nx), _rising(c, nx)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if i >= 1 and le_c[i]:
            pos = 1
        elif i >= 1 and se_c[i]:
            pos = -1
        elif pos == 1 and lx_c[i]:
            pos = 0
        elif pos == -1 and sx_c[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
