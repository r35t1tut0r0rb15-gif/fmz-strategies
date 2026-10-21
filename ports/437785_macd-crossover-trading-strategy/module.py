"""MACD 20 / 40 / 4 histogram zero crossings, broker days, long only: the histogram crossing above zero buys, crossing below zero closes.
Port of FMZ strategy #437785 "MACD Crossover Trading Strategy" (MACD Strategy by Forbes).

FMZ source id: 437785

Source
    https://www.fmz.com/strategy/437785 (PineScript v3, FMZ last modified 2024-01-05 15:32:06).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 144-184), fast 20, slow 40, signal 4; date window true
    delta = (ema 20 - ema 40) - ema(ema 20 - ema 40, 4);  crossover(delta, 0) -> entry Buy;  crossunder(delta, 0) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * window() returns true. Long only. The 100 % of equity size is sizing. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD histogram crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
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

NAME = "fmz_437785_macd_hist_zero_cross_long"
FAMILY = "macd_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 12],
    "slow": [40, 26],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 40, "signal": 4}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    delta = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    up = (delta > 0) & (delta.shift(1) <= 0)
    dn = (delta < 0) & (delta.shift(1) >= 0)
    false = pd.Series(False, index=bars_df.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
