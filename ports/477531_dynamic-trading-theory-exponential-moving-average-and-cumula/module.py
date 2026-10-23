"""Broker days, long only (default direction): the EMA 25 of the close crossing over the EMA 25 of a 100-bar rolling VWAP of hlc3 goes long; crossing back under closes it.
Port of FMZ strategy #477531 "Dynamic Trading Theory Exponential Moving Average and Cumulative Volume Period Crossover Strategy" ([Sapphire] EMA/CVP Strategy).

FMZ source id: 477531

Source
    https://www.fmz.com/strategy/477531 (PineScript v5, FMZ last modified 2025-01-06 11:45:38).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 98-227), EMA 25; cumulative-volume period 100 (rolling sums); exit type Crossover; direction LONG; time filter off
    cumValue = sum(hlc3 x volume, 100) / sum(volume, 100);  longEntryCondition = crossover(ema(close, 25), ema(cumValue, 25)) and tradeDirection == 'LONG' -> entry Long
    position_size > 0 and crossunder(ema(close, 25), ema(cumValue, 25)) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The defaults trade long only (direction LONG), with the Crossover exit; the time filter and the
      end-of-window close are off. The entry and the close cross in opposite directions, so they never
      meet on one bar. Long only. Capital, qty 1 and the per-contract commission are sizing and costs.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA of price against the EMA of a rolling VWAP.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: capital, qty 1 and commission stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) as the rolling-VWAP weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477531_ema25_vs_ema_rolling_vwap100_cross_long_only"
FAMILY = "vwap"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [25, 50],
    "cvp": [100, 50],
}
DEFAULT_PARAMS = {"ema_len": 25, "cvp": 100}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    n, k = int(p["cvp"]), int(p["ema_len"])
    cum = ((h + lo + c) / 3 * v).rolling(n).sum() / v.rolling(n).sum()
    e = c.ewm(span=k, adjust=False).mean()
    ec = cum.ewm(span=k, adjust=False).mean()
    buy = (e > ec) & (e.shift(1) <= ec.shift(1))
    ex = (e < ec) & (e.shift(1) >= ec.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), ex.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
