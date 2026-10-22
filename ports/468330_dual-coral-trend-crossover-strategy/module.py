"""Coral trend crossings, daily bars, long only: the fast coral line (3) crossing over the slow one (6) buys; nothing ever sells.
Port of FMZ strategy #468330 "Dual Coral Trend Crossover Strategy" (D-Stryker LT).

FMZ source id: 468330

Source
    https://www.fmz.com/strategy/468330 (PineScript v5, FMZ last modified 2024-09-26 16:00:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 115-151), coral trend = EMA of EMA + 0.2 x (EMA - EMA of EMA), periods 3 / 6
    crossover(coral3, coral6) -> entry Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script has no exit at all: the first cross-up opens a long held to the end of the data and
      later entries do nothing, as written (as #451391). Long only. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, coral trend crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_468330_coral3_6_cross_no_exit_long"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "p1": [3, 5],
    "p2": [6, 12],
}
DEFAULT_PARAMS = {"p1": 3, "p2": 6, "d": 0.2}


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


def _coral(c, n, d):
    e = c.ewm(span=int(n), adjust=False).mean()
    ee = e.ewm(span=int(n), adjust=False).mean()
    return ee + d * (e - ee)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a, b = _coral(c, p["p1"], float(p["d"])), _coral(c, p["p2"], float(p["d"]))
    le = (a > b) & (a.shift(1) <= b.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
