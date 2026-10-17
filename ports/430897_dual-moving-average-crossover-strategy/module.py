"""SMA 10 / 13 crosses (chiragchopra91), broker days: the SMA 10 crossing above the SMA 13 goes long, crossing below goes
short; each position has a 1 % stop from its entry price.
Port of FMZ strategy #430897 "Dual Moving Average Crossover Strategy" (Chirag Strategy SMA).

FMZ source id: 430897

Source
    https://www.fmz.com/strategy/430897 (PineScript v4, FMZ last modified 2023-11-02 17:04:55).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 149-177), SMA 10 / 13, stop 1 % each side
    crossover(sma(close, 10), sma(close, 13)) -> close short, entry long
    crossover(sma(close, 13), sma(close, 10)) -> close long, entry short
    long: exit(stop = avg price x 0.99);  short: exit(stop = avg price x 1.01)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stops are fixed fractions of the entry price: sl_stop 0.01 for both sides; vbt applies them
      from the fill bar, while the source places them one bar later (position_size checked on the
      bar close), as #365892.
    * strategy.close before the opposite entry ends in the same reversal: REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed percentage stop.
    2 generic: PASS, SMA crosses and a percentage stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_430897_sma_10_13_cross_stop"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "slow": [13, 30],
    "stop_pct": [1.0, 3.0],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 13, "stop_pct": 1.0}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    dn = ((s > f) & (s.shift(1) <= f.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
