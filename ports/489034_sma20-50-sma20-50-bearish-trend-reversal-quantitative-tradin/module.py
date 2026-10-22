"""SMA 20 / 50 crossings, broker days, short only: the down-cross goes short, the up-cross closes.
Port of FMZ strategy #489034 "均线交叉空头反转量化策略SMA20-50-智能空单交易系统-SMA20-50-Bearish-Trend-Reversal-Quantitative-Trading-System" (SMA20/50 Short-Only Strategy).

FMZ source id: 489034

Source
    https://www.fmz.com/strategy/489034 (PineScript v6, FMZ last modified 2025-04-01 13:45:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 109-152), SMA 20 / 50; capital 5000, 100 % of equity
    crossunder(sma20, sma50) -> entry Short;  crossover(sma20, sma50) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Short only. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: capital 5000, 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Short only: Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489034_sma20_50_cross_short"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50}


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
    se = (f < s) & (f.shift(1) >= s.shift(1))
    sx = (f > s) & (f.shift(1) <= s.shift(1))
    false = pd.Series(False, index=c.index)
    return false, false.copy(), se, sx


def portfolio_kwargs(**params):
    return {}
