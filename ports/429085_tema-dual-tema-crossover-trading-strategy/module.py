"""TEMA 20 / TEMA 60 state, long only, broker days: the fast TEMA above the slow one holds a long, below it the
long is closed.
Port of FMZ strategy #429085 "双TEMA叉死叉交易策略Dual-TEMA-Crossover-Trading-Strategy" (TEMA Cross Backtest).

FMZ source id: 429085

Source
    https://www.fmz.com/strategy/429085 (PineScript v4, FMZ last modified 2023-10-12 17:34:19).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 226-254), TEMA 20 / 60 on close
    tema(n) = 3 ema1 - 3 ema2 + ema3; xnRes > ynRes -> entry long; xnRes < ynRes -> close long (shorts commented out)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short side is commented out: long only. The window is dropped (window() is true).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average comparisons only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() capital and 100 % of equity stored.
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

NAME = "fmz_429085_tema_20_60_long"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "slow": [60, 100],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 60}


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


def _tema(x, n):
    e1 = x.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    e3 = e2.ewm(span=n, adjust=False).mean()
    return 3 * e1 - 3 * e2 + e3


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = _tema(c, int(p["fast"])), _tema(c, int(p["slow"]))
    long_e = (f > s).astype(bool)
    long_x = (f < s).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
