"""Broker days: the SMA 14 crossing over the SMA 28 goes long, crossing under goes short; the opposite signal reverses.
Port of FMZ strategy #483515 "24小时量价结合斐波那契回调交叉均线交易策略-24-Hour-Volume-Price-Fibonacci-Retracement-MA-Cross-Trading-Strategy" (24-Hour Volume and Fibonacci Levels Strategy).

FMZ source id: 483515

Source
    https://www.fmz.com/strategy/483515 (PineScript v5, FMZ last modified 2025-02-24 09:55:47).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 110-152), SMA 14 / 28; "24-hour" high / low and Fibonacci levels plotted only; volume SMA plotted only
    longCondition = crossover(sma(close, 14), sma(close, 28)) -> entry My Long Entry Id;  shortCondition = crossunder(...) -> entry My Short Entry Id

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "24-hour" high and low never reset (on daily bars every bar is inside its own day window), and
      they, the Fibonacci levels and the volume average only plot: volume is not used (held for volume,
      not used). Entries only; an opposite entry reverses. REVERSAL INTENDED. No sizing code. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA 14 / 28 crossings.
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

NAME = "fmz_483515_sma14_28_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [14, 10],
    "slow": [28, 50],
}
DEFAULT_PARAMS = {"fast": 14, "slow": 28}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    buy = (f > s) & (f.shift(1) <= s.shift(1))
    sell = (f < s) & (f.shift(1) >= s.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
