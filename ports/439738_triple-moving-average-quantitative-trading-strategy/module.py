"""SMA 13 / 50 crossings on the SMA 200 side, broker days: the SMA 13 crossing over the SMA 50 with the close above the SMA 200 goes long, crossing under with the close below it goes short; reversing.
Port of FMZ strategy #439738 "Triple Moving Average Quantitative Trading Strategy" (Custom MA Strategy Tester).

FMZ source id: 439738

Source
    https://www.fmz.com/strategy/439738 (PineScript v4, FMZ last modified 2024-01-23 14:20:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 128-233), MA1 SMA 13, MA2 SMA 50, MA3 SMA 200 of close; trading window 2019-01-01 to 2025-01-01
    if time in [2019-01-01, 2025-01-01]: crossover(MA1, MA2) and close > MA3 -> entry Long;  crossunder(MA1, MA2) and close < MA3 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The author's fixed trading window (2019 to 2025) is a backtest range, dropped as earlier ports drop
      date windows. strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings and an SMA side.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_439738_sma13_50_cross_sma200_side"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1": [13, 20],
    "ma2": [50, 100],
}
DEFAULT_PARAMS = {"ma1": 13, "ma2": 50, "ma3": 200}


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
    a, b, t = (c.rolling(int(p[k])).mean() for k in ("ma1", "ma2", "ma3"))
    up = (a > b) & (a.shift(1) <= b.shift(1)) & (c > t)
    dn = (a < b) & (a.shift(1) >= b.shift(1)) & (c < t)
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
