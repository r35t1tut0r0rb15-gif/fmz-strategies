"""Power-stretched stochastic, broker days: the raw stochastic (14) pushed away from 50 by a power of 0.25; crossing over 20 goes long, crossing under 80 goes short; reversing.
Port of FMZ strategy #439246 "Exponential Smoothed Stochastic Oscillator Strategy" (Exponential Stochastic Strategy).

FMZ source id: 439246

Source
    https://www.fmz.com/strategy/439246 (PineScript v5, FMZ last modified 2024-01-18 15:53:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 150-176), length 14; exp input 2 (power 2 / 8 = 0.25); bottom 20, top 80
    s = 100 (close - lowest(low, 14)) / (highest(high, 14) - lowest(low, 14));  ks = 50 +/- |s - 50| ^ e / 50 ^ (e - 1), e = ex / (10 - ex)
    crossover(ks, 20) and bar_index > 0 -> entry long;  crossunder(ks, 80) and bar_index > 0 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A range of zero leaves the stochastic undefined (no signal). strategy.entry reverses: REVERSAL
      INTENDED. The 100 % of equity size is sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic levels.
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

NAME = "fmz_439246_power_stochastic_20_80_cross"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21],
    "ex": [2, 5],
}
DEFAULT_PARAMS = {"length": 14, "ex": 2, "bot": 20, "top": 80}


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
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        s = 100 * (c - ll) / (hh - ll)
    s = s.where(np.isfinite(s))
    ex = int(p["ex"])
    e = ex / (10 - ex) if ex < 10 else 99.0
    dist = (s - 50).abs() ** e / 50 ** (e - 1)
    ks = (50 + dist).where(s > 50, 50 - dist)
    ks = ks.where(s.notna())
    b, t = float(p["bot"]), float(p["top"])
    first = pd.Series(np.arange(len(c)) > 0, index=c.index)
    up = (ks > b) & (ks.shift(1) <= b) & first
    dn = (ks < t) & (ks.shift(1) >= t) & first
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
