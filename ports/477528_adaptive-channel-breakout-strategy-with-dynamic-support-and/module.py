"""Closes within 1 % of the 20-bar low, broker days, long only: such a close buys, with a 1.5 % stop and 3 % target from the entry price.
Port of FMZ strategy #477528 "Adaptive Channel Breakout Strategy with Dynamic Support and Resistance Trading System" (Support and Resistance with Trend Lines and Channels).

FMZ source id: 477528

Source
    https://www.fmz.com/strategy/477528 (PineScript v5, FMZ last modified 2025-01-06 11:40:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-187), support / resistance lookback 20; channel width 0.01 % (drawn only); stop 1.5 %, target 3 % of strategy.position_avg_price
    close <= lowest(low, 20) x 1.01 -> entry Buy;  in a long: exit(Buy, stop = avg x 0.985, limit = avg x 1.03)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 20-bar low includes the current bar, as written. The condition is a state, so the entry
      repeats; it is ignored while long and re-enters on the next such bar after a bracket exit. The
      bracket is sent from the position's average price while it is held: a scalar fraction of the entry
      fill, active from the fill (as #440797). The lines and labels are drawn only. Long only. Stop
      module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; avg-price bracket as fractions of the fill.
    2 generic: PASS, near-support buys with a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_477528_near_20bar_low_pct_bracket_long"
FAMILY = "support_resistance"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [20, 50],
    "tp_pct": [0.03, 0.06],
}
DEFAULT_PARAMS = {"lookback": 20, "tp_pct": 0.03, "sl_pct": 0.015, "near": 0.01}


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
    lo, c = bars_df["low"], bars_df["close"]
    sup = lo.rolling(int(p["lookback"])).min()
    le = c <= sup * (1 + float(p["near"]))
    false = pd.Series(False, index=c.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
