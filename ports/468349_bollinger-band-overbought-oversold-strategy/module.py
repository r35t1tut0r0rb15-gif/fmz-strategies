"""Bollinger %b dips above the SMA 200, daily bars, long only: three closes in a row with %b under 0.2 while the close is over the SMA 200 buy; a %b over 0.8 sells.
Port of FMZ strategy #468349 "Bollinger Band Overbought Oversold Strategy" (Larry Connors %b Strategy (Bollinger Band)).

FMZ source id: 468349

Source
    https://www.fmz.com/strategy/468349 (PineScript v5, FMZ last modified 2024-09-26 17:18:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 136-189), SMA 200; BB 20, 2 sd (population); %b = (close - lower) / (upper - lower); levels 0.2 / 0.8 (constants)
    close > sma200 and %b < 0.2 on this bar and the 2 before -> entry Buy;  %b > 0.8 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry and exit tests cannot hold on the same bar. Long only. No sizing code. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, %b dips in an uptrend.
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

NAME = "fmz_468349_connors_percent_b_three_day_dip_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 10],
    "low_b": [0.2, 0.1],
    "high_b": [0.8, 0.5],
}
DEFAULT_PARAMS = {"length": 20, "low_b": 0.2, "high_b": 0.8}


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
    dev = c.rolling(n).std(ddof=0)
    lower, upper = basis - 2 * dev, basis + 2 * dev
    pb = (c - lower) / (upper - lower)
    lb = float(p["low_b"])
    le = (c > c.rolling(200).mean()) & (pb.shift(2) < lb) & (pb.shift(1) < lb) & (pb < lb)
    lx = pb > float(p["high_b"])
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
