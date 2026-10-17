"""Fibonacci retracement crosses (Zer3192), broker days, long only: the close crossing above the 61.8 % retracement of the
50-bar range goes long; the close crossing below the 23.6 % retracement closes the long.
Port of FMZ strategy #430984 "斐波那契回撤交易策略脚本" (斐波那契回撤交易策略).

FMZ source id: 430984

Source
    https://www.fmz.com/strategy/430984 (PineScript v5, FMZ last modified 2023-11-03 15:30:58).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 35-58), range 50, levels 0.236 / 0.618
    fibLevel1 = highest(high, 50) - range x 0.236;  fibLevel3 = highest(high, 50) - range x 0.618
    crossover(close, fibLevel3) -> entry "Buy";  crossunder(close, fibLevel1) -> close "Buy"

Interpretation choices (Pine rules in SURVEY_README.md)
    * The range includes the current bar. The two crosses cannot happen on one bar (the 23.6 % level is
      above the 61.8 % one). Long only; Opposite entries cannot occur. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, retracement fractions of a rolling range.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG430984 (2 members, best partner #432798, Jaccard 0.885); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430984_fib_retracement_cross_long"
FAMILY = "pivot_levels"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 100],
    "entry_fib": [0.618, 0.5],
}
DEFAULT_PARAMS = {"length": 50, "entry_fib": 0.618, "exit_fib": 0.236}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    rng = hh - ll
    f_in, f_out = hh - rng * p["entry_fib"], hh - rng * p["exit_fib"]
    entry = ((c > f_in) & (c.shift(1) <= f_in.shift(1))).astype(bool)
    exit_ = ((c < f_out) & (c.shift(1) >= f_out.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return entry, exit_, false, false.copy()


def portfolio_kwargs(**params):
    return {}
