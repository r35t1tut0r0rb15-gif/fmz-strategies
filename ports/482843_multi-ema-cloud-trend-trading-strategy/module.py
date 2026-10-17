"""EMA 9 / 21 cloud, long only, daily (broker-day) bars: long while the close is above EMA 9 and EMA 9 above EMA 21;
closed when the close is below EMA 9 and EMA 9 below EMA 21.
Port of FMZ strategy #482843 "多重均线云层趋势交易策略-Multi-EMA-Cloud-Trend-Trading-Strategy" (EMA Cloud Strategy).

FMZ source id: 482843

Source
    https://www.fmz.com/strategy/482843 (PineScript v5, FMZ last modified 2025-02-20 14:48:05).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 108-140), EMA 9 / 21 (EMA 200 only plotted)
    bullish = close > ema9 and ema9 > ema21 -> entry long; bearish = close < ema9 and ema9 < ema21 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every bullish bar is an entry signal (same-side ignored while held). Long only; no stops. Daily bars are broker
      days (17:00 America/New_York) stamped with their first minute (as #430984). FREQ = "1D" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482843_ema9_21_cloud_long_1d"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 12],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    long_e = ((c > f) & (f > s)).astype(bool)
    long_x = ((c < f) & (f < s)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
