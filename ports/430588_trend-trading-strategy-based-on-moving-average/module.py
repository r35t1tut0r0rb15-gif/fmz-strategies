"""A 400-bar VWMA of hl2 above all of its previous 5 values, broker days, long only: while rising it holds a long, otherwise it closes (the same rule as #430385, with a quarterly table).
Port of FMZ strategy #430588 "Trend Trading Strategy Based on Moving Average" (Quarterly Returns in Strategies vs Buy & Hold).

FMZ source id: 430588

Source
    https://www.fmz.com/strategy/430588 (PineScript v4, FMZ last modified 2023-10-30 15:53:25).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 190-202), VWMA 400 of hl2; rising over 5 bars; the quarterly table only reports
    uptrend = rising(vwma(hl2, 400), 5) -> entry Buy;  else -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The same trading rule as #430385 (a different author's copy with a quarterly report). ta.rising(x, 5)
      is read as above every one of the previous 5 values. Long only. The 100 % of equity size and
      commission are sizing / costs. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, long VWMA slope trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, capital 1000, commission 0.1 % stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in vwma(hl2, 400); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430588_vwma400_hl2_rising5_long_quarterly_copy"
FAMILY = "ma_slope"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_length": [400, 300],
    "rise_len": [5, 3],
}
DEFAULT_PARAMS = {"ma_length": 400, "rise_len": 5}


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
    h, lo, v = bars_df["high"], bars_df["low"], bars_df["volume"]
    n = int(p["ma_length"])
    w = ((h + lo) / 2 * v).rolling(n).sum() / v.rolling(n).sum()
    up = w > w.shift(1).rolling(int(p["rise_len"])).max()
    false = pd.Series(False, index=w.index)
    return up, ~up, false, false.copy()


def portfolio_kwargs(**params):
    return {}
