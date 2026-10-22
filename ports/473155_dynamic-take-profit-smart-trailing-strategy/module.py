"""Intrabar drops, daily bars, long only: a bar whose low falls 0.98 % or more under its open buys at the next open, with a 1.23 % target from the fill.
Port of FMZ strategy #473155 "Dynamic Take Profit Smart Trailing Strategy" (Price Drop Buy Signal Strategy).

FMZ source id: 473155

Source
    https://www.fmz.com/strategy/473155 (PineScript v5, FMZ last modified 2024-11-27 16:41:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-119), drop -0.98 % of the open; target 1.23 % of the average price; trail_offset = avg x 0.6 % (a price passed as ticks, no trail price or points)
    low <= open x (1 - 0.0098) -> entry Long;  while long: exit(limit = avg x 1.0123, trail_offset = avg x 0.006)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The signal is read at the bar's close and filled at the next open. The target comes from the
      average (fill) price and is sent every bar while held: ported active from the fill bar (#440797)
      as the fixed fraction 0.0123. trail_offset without trail_price / trail_points places no trailing
      stop (#441084). There is no stop. Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on
      daily bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the fill-price target as a fixed fraction.
    2 generic: PASS, intrabar drop buys with a small target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_473155_intrabar_drop_buy_pct_target_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "drop_pct": [0.0098, 0.02],
    "tp_pct": [0.0123, 0.03],
}
DEFAULT_PARAMS = {"drop_pct": 0.0098, "tp_pct": 0.0123}


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
    le = bars_df["low"] <= bars_df["open"] * (1 - float(p["drop_pct"]))
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
