"""Close / SMA 50 crossings, broker days: the close crossing over the SMA 50 goes long, crossing under goes short; reversing (the London session times are computed but never used).
Port of FMZ strategy #439262 "基于伦敦SMA交叉的ETH反转交易策略London-SMA-Cross-ETH-Reversal-Trading-Strategy" (London SMA Strategy).

FMZ source id: 439262

Source
    https://www.fmz.com/strategy/439262 (PineScript v5, FMZ last modified 2024-01-18 16:08:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 131-172), SMA 50 of close; London session 06:59-15:59 and the 2021 start (unused)
    long_condition = crossover(close, sma 50);  short_condition = crossunder(close, sma 50);  entry Long / entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * in_london_session and in_backtesting_range are computed but no order reads them. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close / SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); the London times unused.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439262_close_sma50_cross_daily"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_length": [50, 20, 100],
}
DEFAULT_PARAMS = {"sma_length": 50}


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
    s = c.rolling(int(p["sma_length"])).mean()
    up = (c > s) & (c.shift(1) <= s.shift(1))
    dn = (c < s) & (c.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
