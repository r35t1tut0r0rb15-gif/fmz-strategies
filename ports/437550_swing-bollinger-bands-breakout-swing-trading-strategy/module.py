"""Bollinger breakout swing, broker days, long only: a close above the upper band (SMA 20 + 2 sigma) buys; a close under the middle band closes the long.
Port of FMZ strategy #437550 "布林带突破-Swing-交易策略Bollinger-Bands-Breakout-Swing-Trading-Strategy" (Bollinger Bands Breakout Strategy).

FMZ source id: 437550

Source
    https://www.fmz.com/strategy/437550 (PineScript v5, FMZ last modified 2024-01-03 16:40:38).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 138-163), length 20, source close, multiplier 2
    close > upper -> entry Buy;  close < basis -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * stdev is the population deviation. A same-side entry while long is ignored (pyramiding 0). Long only.
      No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437550_bollinger_breakout_mid_exit_long"
FAMILY = "bollinger_breakout"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    up = basis + float(p["mult"]) * c.rolling(n).std(ddof=0)
    false = pd.Series(False, index=bars_df.index)
    return c > up, c < basis, false, false.copy()


def portfolio_kwargs(**params):
    return {}
