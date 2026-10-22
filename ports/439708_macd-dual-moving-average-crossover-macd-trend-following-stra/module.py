"""MACD green / red states, long only, broker days: the MACD (12, 26) above both its signal and zero holds a long; below both closes it; the entry is sent on every bar of the state.
Port of FMZ strategy #439708 "双移动平均线交叉MACD趋势跟踪策略Dual-Moving-Average-Crossover-MACD-Trend-Following-Strategy" (MACD Trend Follow Strategy).

FMZ source id: 439708

Source
    https://www.fmz.com/strategy/439708 (PineScript v4, FMZ last modified 2024-01-23 11:22:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 147-214), long only; MACD 12 / 26 / 9, EMA oscillator and signal; date window true
    Green = macd > signal and macd > 0;  Red = macd < signal and macd < 0;  Long only: entry L on Green;  close L on Red

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long-only branch of the script; the two states cannot share a bar. A same-side entry while in
      the position is ignored. Long only. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD states.
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

NAME = "fmz_439708_macd_green_red_state_long"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_length": [12, 8],
    "slow_length": [26, 21],
}
DEFAULT_PARAMS = {"fast_length": 12, "slow_length": 26, "signal_length": 9}


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
    macd = c.ewm(span=int(p["fast_length"]), adjust=False).mean() - c.ewm(span=int(p["slow_length"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal_length"]), adjust=False).mean()
    green = (macd > sig) & (macd > 0)
    red = (macd < sig) & (macd < 0)
    false = pd.Series(False, index=c.index)
    return green, red, false, false.copy()


def portfolio_kwargs(**params):
    return {}
