"""Closes against the previous bar's 50 % level and recent extremes, daily bars: a close over the previous bar's open plus half its range and over the prior 20-bar low goes long, a close under that level and under the prior 10-bar high goes short; reversing.
Port of FMZ strategy #473234 "高级时间框架Fibonacci回撤与高低点条件突破交易系统-Advanced-Timeframe-Fibonacci-Retracement-with-High-Low-Breakout-Trading-System" (Fibonacci Levels Strategy with High/Low Criteria).

FMZ source id: 473234

Source
    https://www.fmz.com/strategy/473234 (PineScript v5, FMZ last modified 2024-11-28 15:01:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-173), higher time frame "D" (the chart itself), "Last" candle; levels open + (high - low) x 0 / 0.236 / ... ; lowest(low, 20)[1], highest(high, 10)[1]
    close > lowest(low, 20)[1] and close > open_ + (high_ - low_) x 0.5 -> entry Long;  close < highest(high, 10)[1] and close < that level -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * On a daily chart the "D" candle starts on every bar, so the "Last" candle is the previous bar:
      the level is open[1] + (high[1] - low[1]) x 0.5, as written (measured from the open). The tests are
      states: repeated entries while held do nothing. There is no exit: positions end at the opposite
      entry. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, previous-bar level and extreme filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473234_prev_bar_half_range_level_extremes_reversal"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "low_look": [20, 50],
    "high_look": [10, 20],
    "level": [0.5, 0.618],
}
DEFAULT_PARAMS = {"low_look": 20, "high_look": 10, "level": 0.5}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    lvl = o.shift(1) + (h.shift(1) - lo.shift(1)) * float(p["level"])
    lowc = lo.rolling(int(p["low_look"])).min().shift(1)
    highc = h.rolling(int(p["high_look"])).max().shift(1)
    le = (c > lowc) & (c > lvl)
    se = (c < highc) & (c < lvl)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
