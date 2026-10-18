"""Bollinger band crossings in either direction, broker days: the close crossing over the upper OR the lower band goes long; crossing under the upper or the lower band goes short (reversing).
Port of FMZ strategy #436489 "Dual Bollinger Band Volatility Tracking Strategy" (BB_BB).

FMZ source id: 436489

Source
    https://www.fmz.com/strategy/436489 (PineScript v3, FMZ last modified 2023-12-25 11:49:41).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 123-152), Bollinger 20 / 2 sd
    buy = crossover(close, upper) or crossover(close, lower);  sell = crossunder(close, upper) or crossunder(close, lower);  entry long (buy), entry short (sell)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Crossing back over the lower band (a recovery) and crossing over the upper band (a breakout) both
      buy; the mirror sells, as written. The date window is always true. REVERSAL INTENDED. The full-equity
      size is sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
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

NAME = "fmz_436489_bollinger_either_band_cross"
FAMILY = "bollinger_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 30],
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
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    xo = lambda a, b: (a > b) & (a.shift(1) <= b.shift(1))      # noqa: E731
    xu = lambda a, b: (a < b) & (a.shift(1) >= b.shift(1))      # noqa: E731
    buy = (xo(c, upper) | xo(c, lower)).fillna(False).astype(bool)
    sell = (xu(c, upper) | xu(c, lower)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
