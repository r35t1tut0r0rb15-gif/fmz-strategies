"""Donchian position trend, broker days: minus the sum of the distances from the close to the 42-bar high and low is
smoothed by an EMA 5 and an EMA 45; the fast crossing above the slow goes long, crossing below goes short.
Port of FMZ strategy #433561 "Donchian Trend Strategy" (DON-SS-TREND).

FMZ source id: 433561

Source
    https://www.fmz.com/strategy/433561 (PineScript v5, FMZ last modified 2023-11-28 15:13:00).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 139-174), Donchian 42; EMA 45 (slow) and 5 (fast) of -(upper - close + lower - close)
    dontrend = (upper - close) + (lower - close);  emax = ema(-dontrend, 45);  emax1 = ema(-dontrend, 5)
    crossover(emax1, emax) -> entry long (and close short);  crossunder -> entry short (and close long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.highest / ta.lowest default to the highs and lows. The value is a price difference, but only
      its crosses with its own average are used, so it is scale-free.
    * REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, crosses of a channel-position line with its average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and the commission stored.
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

NAME = "fmz_433561_donchian_position_trend"
FAMILY = "donchian_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [42, 20],
    "slow": [45, 90],
}
DEFAULT_PARAMS = {"length": 42, "slow": 45, "fast": 5}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    dt = (h.rolling(n).max() - c) + (lo.rolling(n).min() - c)
    slow = (-dt).ewm(span=int(p["slow"]), adjust=False).mean()
    fast = (-dt).ewm(span=int(p["fast"]), adjust=False).mean()
    le = ((fast > slow) & (fast.shift(1) <= slow.shift(1))).astype(bool)
    se = ((fast < slow) & (fast.shift(1) >= slow.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
