"""MACD 12 / 26 / 9 histogram runs, daily bars, long only (the default "MACD" type): three rising histogram bars in a row buy, two falling bars in a row sell.
Port of FMZ strategy #474632 "Multi Strategy Technical Analysis Trading System" (Multi-Strategy Trading System).

FMZ source id: 474632

Source
    https://www.fmz.com/strategy/474632 (PineScript v5, FMZ last modified 2024-12-11 11:06:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-183), strategy type MACD (default); MACD 12 / 26 / 9
    hist[3] < hist[2] < hist[1] < hist -> entry MACD Buy;  hist[2] > hist[1] > hist -> close MACD Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The other three types (a weekly EMA 8 breakout, an EMA ribbon pullback, an MA 100 dip, each
      with its own stop) are separate settings, not ported (default MACD). The entry and close tests
      cannot hold on one bar. Long only. No sizing code. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD histogram runs.
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

NAME = "fmz_474632_macd_hist_three_up_two_down_long"
FAMILY = "macd_momentum"  # proposed 2026-10-22 (FMZ-C), user to confirm
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
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    h1, h2, h3 = hist.shift(1), hist.shift(2), hist.shift(3)
    le = h3.notna() & (h3 < h2) & (h2 < h1) & (h1 < hist)
    lx = h2.notna() & (h2 > h1) & (h1 > hist)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
