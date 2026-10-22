"""Detrended price oscillator crossings, daily bars, long only: DPO (close minus the SMA 24 of 13 bars ago) crossing over its EMA 4 buys, crossing under sells.
Port of FMZ strategy #474030 "DPO-EMA趋势交叉量化策略研究-DPO-EMA-Trend-Crossover-Quantitative-Strategy-Research" (DPO 4,24 Strategy).

FMZ source id: 474030

Source
    https://www.fmz.com/strategy/474030 (PineScript v5, FMZ last modified 2024-12-05 14:57:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-134), SMA 24 shifted 13 (24 / 2 + 1); EMA 4 (constants)
    dpo = close - sma24[13];  crossover(dpo, ema4(dpo)) -> entry Buy;  crossunder -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * length / 2 + 1 = 13. Long only. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, DPO crossings of its EMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474030_dpo24_ema4_cross_long"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    c = bars_df["close"]
    dpo = c - c.rolling(24).mean().shift(13)
    e = dpo.ewm(span=4, adjust=False).mean()
    le = (dpo > e) & (dpo.shift(1) <= e.shift(1))
    lx = (dpo < e) & (dpo.shift(1) >= e.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
