"""Turtle-style close breakouts, broker days: a close above the highest close of the previous 20 days goes long; a close at
or below the lowest close of the previous 10 days closes the long and goes short; a close above the highest close of the
previous 10 days closes the short.
Port of FMZ strategy #434192 "Turtle Breakout Strategy" (TurtleBC Strategy v2 V.Troussel).

FMZ source id: 434192

Source
    https://www.fmz.com/strategy/434192 (PineScript v3, FMZ last modified 2023-12-04 16:25:53).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 159-182), enter 20, exit 10, short exit 10 (closes)
    enterL1 = close > highest(close, 20)[1] -> entry long;  exitL1 = close <= lowest(close, 10)[1] -> close long and entry short
    exitS = close > highest(close, 10)[1] -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each bar: the closes act on the position held at the start of the bar, then an entry wins (a
      long entry also closes a short; a short entry reverses a long). REVERSAL INTENDED. The date
      window (from 2016) is open. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close-channel breaks.
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

NAME = "fmz_434192_turtle_close_breakout"
FAMILY = "donchian_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "enter_len": [20, 55],
    "exit_len": [10, 20],
}
DEFAULT_PARAMS = {"enter_len": 20, "exit_len": 10}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ex = int(p["exit_len"])
    el = (c > c.rolling(int(p["enter_len"])).max().shift(1)).to_numpy()
    xl = (c <= c.rolling(ex).min().shift(1)).to_numpy()
    xs = (c > c.rolling(ex).max().shift(1)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 1 and xl[i]:
            pos = 0
        elif pos == -1 and xs[i]:
            pos = 0
        if el[i]:
            pos = 1
        elif xl[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
