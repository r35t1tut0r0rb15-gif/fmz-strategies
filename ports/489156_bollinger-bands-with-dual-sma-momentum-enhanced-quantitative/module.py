"""Broker days, long only: a close over the upper Bollinger 21 / 2 band and the SMA 45 with the SMA 6 over the SMA 45 goes long; a close under the lower band or the SMA 6 under the SMA 45 closes.
Port of FMZ strategy #489156 "Bollinger Bands with Dual SMA Momentum Enhanced Quantitative Trading Strategy" (BTC Bollinger Bands w Fast and Slow SMAs).

FMZ source id: 489156

Source
    https://www.fmz.com/strategy/489156 (PineScript v6, FMZ last modified 2025-04-02 11:28:15).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 162-215), BB 21 / 2 (SMA); SMA 6 / 45; commission 0.1, slippage 3; 100 % of equity
    close > upper and close > sma45 and sma6 > sma45 -> entry Long;  close < lower or sma6 < sma45 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are states. Long only. The commission and slippage are costs. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger breakouts with an SMA trend filter.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity, commission and slippage stored, not ported.
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

NAME = "fmz_489156_bb21_2_upper_breakout_sma6_45_trend_long"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 50],
    "slowSmaLength": [45, 100],
}
DEFAULT_PARAMS = {"length": 21, "slowSmaLength": 45, "fastSmaLength": 6, "mult": 2.0}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    f = c.rolling(int(p["fastSmaLength"])).mean()
    s = c.rolling(int(p["slowSmaLength"])).mean()
    le = (c > basis + dev) & (c > s) & (f > s)
    lx = ((c < basis - dev) | (f < s)) & ~le
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
