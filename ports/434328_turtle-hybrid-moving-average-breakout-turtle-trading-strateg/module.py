"""A 6-bar turtle breakout on broker days: a high above the previous 6-bar highest high goes long, a low under the previous 6-bar lowest low goes short; reversing.
Port of FMZ strategy #434328 "混合均线突破Turtle交易策略Hybrid-Moving-Average-Breakout-Turtle-Trading-Strategy" (Gui's Turtle).

FMZ source id: 434328

Source
    https://www.fmz.com/strategy/434328 (PineScript v4, FMZ last modified 2023-12-05 15:01:56).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 146-398), TurtleSpeed 6; SMAs 10-200, VWMA 200 bands x 3, weekly VWAP bands, pivots and CM SAR are plots only
    FastSpeed = highest(6), SlowSpeed = lowest(6);  high > FastSpeed[1] -> entry Long;  low < SlowSpeed[1] -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the turtle breakout trades; the VWMA bands, weekly VWAP bands, pivot zones and SARs only feed
      plots, so volume is not used. The author asks for Heikin-Ashi candles in a comment; the port runs on
      the plain candles of the header chart (as earlier ports). A bar breaking both ways takes the short
      (the later call). REVERSAL INTENDED. 10 contracts default is sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, short-period channel breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): default qty 10, pyramiding 0, not ported.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434328_turtle_6bar_breakout_daily_reversal"
FAMILY = "channel_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "turtle_speed": [6, 20],
}
DEFAULT_PARAMS = {"turtle_speed": 6}


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
    h, lo = bars_df["high"], bars_df["low"]
    n = int(p["turtle_speed"])
    up = h > h.rolling(n).max().shift(1)
    dn = lo < lo.rolling(n).min().shift(1)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return up & ~dn, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
