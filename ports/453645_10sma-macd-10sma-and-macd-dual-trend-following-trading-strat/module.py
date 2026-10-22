"""Joint crossings of the SMA 10 and the MACD, daily bars, long only: a bar where the close crosses over the SMA 10 and the MACD 12 / 26 crosses over its signal buys; a bar with both crossing down sells.
Port of FMZ strategy #453645 "10SMA与MACD双重趋势跟踪交易策略-10SMA-and-MACD-Dual-Trend-Following-Trading-Strategy" (10SMA and MACD Strategy).

FMZ source id: 453645

Source
    https://www.fmz.com/strategy/453645 (PineScript v5, FMZ last modified 2024-06-07 14:46:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 103-135), SMA 10; MACD 12 / 26 / 9
    crossover(close, sma10) and crossover(macd, signal) -> entry Long;  crossunder(close, sma10) and crossunder(macd, signal) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both crossings must fall on the same bar. Long only. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, joint SMA / MACD crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453645_close_sma10_and_macd_joint_cross_long"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20],
    "fast": [12, 8],
    "slow": [26, 21],
}
DEFAULT_PARAMS = {"length": 10, "fast": 12, "slow": 26, "signal": 9}


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
    sma = c.rolling(int(p["length"])).mean()
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    c1 = c.shift(1)
    le = (c > sma) & (c1 <= sma.shift(1)) & (macd > sig) & (macd.shift(1) <= sig.shift(1))
    lx = (c < sma) & (c1 >= sma.shift(1)) & (macd < sig) & (macd.shift(1) >= sig.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
