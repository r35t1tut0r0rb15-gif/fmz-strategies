"""EMA crossings on one entry id, broker days: the close crossing over the EMA 75 and under the EMA 50 on the same bar with the EMA 10 crossing under the EMA 20 goes short; otherwise the EMA 10 crossing
over the EMA 20 goes long; reversing.
Port of FMZ strategy #442225 "基于EMA均线的短线交易策略Short-term-Trading-Strategy-Based-on-EMA" (Jan 2024 Daily (Short)).

FMZ source id: 442225

Source
    https://www.fmz.com/strategy/442225 (PineScript v5, FMZ last modified 2024-02-20 14:06:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 105-134), EMA 10 / 20 / 50 / 75 / (200 smoothed, plot only); capital 10000, commission 1
    sell = crossover(close, ema75) and crossunder(close, ema50) and crossunder(ema10, ema20) -> entry "daily" short;  else buy = crossover(ema10, ema20) -> entry "daily" long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both entries use the id "daily", so each opposite entry reverses the position. The short needs three
      crossings on one bar, as written. REVERSAL INTENDED. The capital and the commission of 1 are sizing
      and costs. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ
      = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital and commission stored.
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

NAME = "fmz_442225_ema10_20_cross_triple_cross_short_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 5],
    "slow": [20, 30],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 20}


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
    e10 = c.ewm(span=int(p["fast"]), adjust=False).mean()
    e20 = c.ewm(span=int(p["slow"]), adjust=False).mean()
    e50 = c.ewm(span=50, adjust=False).mean()
    e75 = c.ewm(span=75, adjust=False).mean()
    c1 = c.shift(1)
    xo75 = (c > e75) & (c1 <= e75.shift(1))
    xu50 = (c < e50) & (c1 >= e50.shift(1))
    xu1020 = (e10 < e20) & (e10.shift(1) >= e20.shift(1))
    xo1020 = (e10 > e20) & (e10.shift(1) <= e20.shift(1))
    sell = xo75 & xu50 & xu1020
    buy = xo1020 & ~sell
    false = pd.Series(False, index=c.index)
    return buy, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
