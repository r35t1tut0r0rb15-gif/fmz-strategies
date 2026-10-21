"""EMA 50 / 100 crossings, broker days: the EMA 50 crossing over the EMA 100 goes long, crossing under goes short; reversing.
Port of FMZ strategy #438931 "基于EMA-MA交叉的交易策略EMA-MA-Crossover-Options-Trading-Strategy" (Backtest single EMA cross).

FMZ source id: 438931

Source
    https://www.fmz.com/strategy/438931 (PineScript v4, FMZ last modified 2024-01-16 14:14:42).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 158-202), EMA 50 / 100; buy quantity 100000; date window true
    crossover(ema 50, ema 100) -> entry Long;  crossunder -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * testPeriod() is true. strategy.entry reverses: REVERSAL INTENDED. The quantity input is sizing (not
      passed to the orders). Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity input stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG438931 (2 members, best partner #439612, Jaccard 0.963); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438931_ema50_100_cross"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema1": [50, 20],
    "ema2": [100, 200],
}
DEFAULT_PARAMS = {"ema1": 50, "ema2": 100}


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
    f = c.ewm(span=int(p["ema1"]), adjust=False).mean()
    s = c.ewm(span=int(p["ema2"]), adjust=False).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
