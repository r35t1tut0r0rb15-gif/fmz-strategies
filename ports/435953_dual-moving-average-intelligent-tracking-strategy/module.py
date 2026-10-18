"""Moving-average state, broker days, long only: in the default composite mode a rising SMA 50 with the SMA 10 over the SMA 30 buys; a falling
SMA 50 with the SMA 10 under the SMA 30 closes. The crossover-only and direction-only modes are in the grid.
Port of FMZ strategy #435953 "Dual Moving Average Intelligent Tracking Strategy" (Smart MA Strategy).

FMZ source id: 435953

Source
    https://www.fmz.com/strategy/435953 (PineScript v5, FMZ last modified 2023-12-20 13:50:47).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 90-144), base SMA 50, fast 10, slow 30; mode Composite; the MA type input only feeds the colours
    Composite: base rising and fast > slow -> entry long; base not rising and fast < slow -> close;  Crossover: fast > slow -> entry long, fast < slow -> close;  Direction: base rising -> entry, not rising -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "MA Type" input is unused by the orders (SMAs throughout). The date range is the author's
      window (1975 to 2099): dropped. A repeated entry adds nothing. Long only. The 20 % of equity
      size is sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435953_smart_ma_state_long"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "base_ma_length": [50, 100],
    "mode": ["Composite", "Crossover", "Direction"],
}
DEFAULT_PARAMS = {"base_ma_length": 50, "mode": "Composite", "fast": 10, "slow": 30}


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
    fast, slow = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    base = c.rolling(int(p["base_ma_length"])).mean()
    inc = base > base.shift(1)
    mode = p["mode"]
    if mode == "Composite":
        le, lx = inc & (fast > slow), (~inc) & (fast < slow)
    elif mode == "Crossover":
        le, lx = fast > slow, fast < slow
    else:
        le, lx = inc, ~inc
    false = pd.Series(False, index=bars_df.index)
    return le.fillna(False).astype(bool), lx.fillna(False).astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
