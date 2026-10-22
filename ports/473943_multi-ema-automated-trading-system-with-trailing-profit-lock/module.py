"""Stacked EMA breakouts, daily bars, long only: with EMA 50 < EMA 20 of lows < EMA 20 of closes < EMA 20 of highs < EMA 5 and the close over all of them, it buys from flat; a close under the EMA 5 or under the EMA 20 of lows sells.
Port of FMZ strategy #473943 "Multi EMA Automated Trading System with Trailing Profit Lock" (Automated EMA Strategy with Hierarchical Conditions).

FMZ source id: 473943

Source
    https://www.fmz.com/strategy/473943 (PineScript v5, FMZ last modified 2024-12-04 15:35:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-140), EMA 5; EMA 20 of high / low / close; EMA 50 (constants)
    ema50 < ema20L < ema20C < ema20H < ema5 and close over all and not long -> entry Buy;  long and (close < ema5 or close < ema20L) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry and the close cannot hold on one bar (the entry needs the close over the EMA 5). Entries
      only while not long; a repeat entry while long would be ignored anyway. Long only. No sizing
      code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stacked EMA breakouts with close-based exits.
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

NAME = "fmz_473943_stacked_ema5_20hlc_50_breakout_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e5 = c.ewm(span=5, adjust=False).mean()
    eh, el, ec = (x.ewm(span=20, adjust=False).mean() for x in (h, lo, c))
    e50 = c.ewm(span=50, adjust=False).mean()
    le = ((e50 < el) & (el < ec) & (ec < eh) & (eh < e5)
          & (c > e5) & (c > ec) & (c > eh) & (c > el) & (c > e50))
    lx = (c < e5) | (c < el)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
