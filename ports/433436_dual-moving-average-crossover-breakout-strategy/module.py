"""EMA 30 crossing over the EMA 33 goes long, crossing under goes short; broker days, reversing.
Port of FMZ strategy #433436 "Dual Moving Average Crossover Breakout Strategy" (stub (es1!_1minute_hull)).

FMZ source id: 433436

Source
    https://www.fmz.com/strategy/433436 (PineScript v3, FMZ last modified 2023-11-27 16:21:45).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 133-187), EMA 30 / 33 (the volume-weighted versions are commented out); window 2010 .. 2039
    go_long = crossover(ema(close, 30), ema(close, 33));  go_short = crossunder(...)
    go_long -> entry long_ride, close short_ride;  go_short -> entry short_ride, close long_ride

Interpretation choices (Pine rules in SURVEY_README.md)
    * The volume sums are computed but feed only the commented-out volume-weighted EMAs: volume is not
      used. The closes come after the entries and act on the side the opposite entry already reverses.
      The 2010 .. 2039 window is dropped. REVERSAL INTENDED. 100 % of equity is sizing. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, capital 1000000, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); the author's 2010 .. 2039 window dropped.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433436_ema30_ema33_cross_daily_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_len": [30, 20],
    "slow_len": [33, 50],
}
DEFAULT_PARAMS = {"fast_len": 30, "slow_len": 33}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast_len"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow_len"]), adjust=False).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
