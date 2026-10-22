"""Three bars with growing bodies, daily bars: when the third body is the largest and the bar is green go long, red go short; reversing (the SMA 50 / 200 only plot).
Port of FMZ strategy #446433 "Quantitative Trading Strategy Based on Three Consecutive Bullish Bearish Candles and Dual Moving Averages" (Consecutive Candles with MAs (CCMAs)).

FMZ source id: 446433

Source
    https://www.fmz.com/strategy/446433 (PineScript v4, FMZ last modified 2024-03-28 16:22:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 108-140), three increasing bodies; SMA 50 / 200 (plot only)
    |c2 - o2| < |c1 - o1| < |c - o| and close > open -> entry Al;  ... and close < open -> entry Sat

Interpretation choices (Pine rules in SURVEY_README.md)
    * The moving averages only plot. No exit: positions end at the opposite entry. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, growing candle bodies.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_446433_three_growing_bodies_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
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
    o, c = bars_df["open"], bars_df["close"]
    b = (c - o).abs()
    grow = (b.shift(2) < b.shift(1)) & (b.shift(1) < b)
    le = grow & (c > o)
    se = grow & (c < o)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
