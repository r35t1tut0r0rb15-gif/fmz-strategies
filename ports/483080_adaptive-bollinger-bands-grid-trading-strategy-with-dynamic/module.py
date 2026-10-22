"""Bollinger 20 / 2 grid levels, broker days: the close crossing over any of the 4 levels 1-4 % above the lower band goes long, crossing under any of the 4 levels 1-4 % below the upper band goes short; reversing, no other exit.
Port of FMZ strategy #483080 "Adaptive Bollinger Bands Grid Trading Strategy with Dynamic Level Adjustment" (Grid Bot based on Bollinger Bands with Adjustable Levels).

FMZ source id: 483080

Source
    https://www.fmz.com/strategy/483080 (PineScript v6, FMZ last modified 2025-02-27 17:04:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-164), Bollinger 20 x 2.0; grid distance 1 %; 4 levels
    longLevels[i] = lower x (1 + 1 % (i + 1));  shortLevels[i] = upper x (1 - 1 % (i + 1)), i = 0..3
    crossover(close, longLevels[0]) -> entry GridLong;  crossover(close, longLevels[i]) -> entry GridLong<i>;  shorts mirror with crossunder

Interpretation choices (Pine rules in SURVEY_README.md)
    * The extra grid entries use new ids; default pyramiding refuses a second long while long (as
      #441137), so the grid never adds and any level crossing is an entry on its side. A short called on
      the same bar as a long wins (called later, as #437773); the other side reverses (REVERSAL
      INTENDED), no other exit. No sizing code. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, percent grid levels off the Bollinger bands.
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

NAME = "fmz_483080_bb20_2_grid4_1pct_level_cross_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "grid_distance_percent": [1.0, 2.0],
    "length": [20, 40],
}
DEFAULT_PARAMS = {"grid_distance_percent": 1.0, "length": 20, "mult": 2.0, "grid_size": 4}


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
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    upper, lower = basis + float(p["mult"]) * sd, basis - float(p["mult"]) * sd
    g = float(p["grid_distance_percent"]) / 100
    le = pd.Series(False, index=c.index)
    se = pd.Series(False, index=c.index)
    for i in range(int(p["grid_size"])):
        ll, sl = lower * (1 + g * (i + 1)), upper * (1 - g * (i + 1))
        le = le | ((c > ll) & (c.shift(1) <= ll.shift(1)))
        se = se | ((c < sl) & (c.shift(1) >= sl.shift(1)))
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
