"""Bollinger 20 / 2 breakouts, daily bars, long only: from flat, a close over the upper band buys; a close under the lower band sells.
Port of FMZ strategy #474977 "Bollinger Bands Momentum Breakout Adaptive Trend Following Strategy" (Demo GPT - Bollinger Bands).

FMZ source id: 474977

Source
    https://www.fmz.com/strategy/474977 (PineScript v5, FMZ last modified 2024-12-13 11:43:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 114-170), BB 20, 2 sd (SMA basis); date range 2018-2069; 100 % of equity, commission 0.1 %, slippage 3
    flat and close > upper -> entry Long;  long and close < lower -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The date range covers the data. The entry and close cannot hold on one bar; a repeat entry while
      long would be ignored. Long only. The costs and the equity share are not ported. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band breakouts with an opposite-band exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size, commission and slippage stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474977_bb20_upper_break_lower_exit_long"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0}


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
    le = c > basis + dev
    lx = c < basis - dev
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
