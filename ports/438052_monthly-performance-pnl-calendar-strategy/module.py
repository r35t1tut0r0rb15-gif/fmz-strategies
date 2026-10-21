"""Closes beyond the extreme of 20 bars ago, broker days: a close above the high of 20 bars back goes long, a close below the low of 20 bars back goes short; reversing. The monthly P/L table only displays.
Port of FMZ strategy #438052 "Monthly Performance PnL Calendar Strategy" (Monthly Performance).

FMZ source id: 438052

Source
    https://www.fmz.com/strategy/438052 (PineScript v5, FMZ last modified 2024-01-08 16:16:58).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 175-309), length input 20 (unused; the code uses 20); monthly performance table on
    close > high[20] -> entry long;  close < low[20] -> entry short;  the monthly / yearly P/L table is display only

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions compare with the single bar 20 bars back (high[20], low[20]), as written. The
      monthly performance table only displays. strategy.entry reverses: REVERSAL INTENDED. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, comparisons with a past bar's extremes.
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

NAME = "fmz_438052_close_vs_bar20_extremes"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [20, 10, 40, 55],
}
DEFAULT_PARAMS = {"lookback": 20}


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
    k = int(p["lookback"])
    false = pd.Series(False, index=bars_df.index)
    return c > h.shift(k), false, c < lo.shift(k), false.copy()


def portfolio_kwargs(**params):
    return {}
