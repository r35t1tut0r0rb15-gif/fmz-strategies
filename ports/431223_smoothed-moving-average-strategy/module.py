"""Smoothed moving-average turns (PuppyTherapy), broker days: an EMA 60 of an EMA 60 of the close turning up (a local
minimum) goes long, turning down goes short.
Port of FMZ strategy #431223 "Smoothed Moving Average Strategy" (Smooth Moving Average [STRATEGY] @PuppyTherapy).

FMZ source id: 431223

Source
    https://www.fmz.com/strategy/431223 (PineScript v4, FMZ last modified 2023-11-06 10:29:24).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 119-281), MA type EMA, length 60, 2 smoothings, HA source off
    ma = variant(variant(close, "EMA", 60), "EMA", 60)
    long = ma > ma[1] and ma[1] < ma[2] -> entry long;  short = ma < ma[1] and ma[1] > ma[2] -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default type EMA with two passes; the other 15 types (one of them VWMA, which would use
      volume) are not selected by default and not ported. The Heikin Ashi source is off. The 2018
      start is dropped.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a smoothed moving average's turns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND431223 (2 members, best partner #434981, Jaccard 0.715); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431223_double_ema_turns"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [60, 30],
    "loops": [2, 1],
}
DEFAULT_PARAMS = {"length": 60, "loops": 2}


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
    ma = bars_df["close"]
    for _ in range(int(p["loops"])):
        ma = ma.ewm(span=int(p["length"]), adjust=False).mean()
    m1, m2 = ma.shift(1), ma.shift(2)
    lg = ((ma > m1) & (m1 < m2)).astype(bool)
    sh = ((ma < m1) & (m1 > m2)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return lg, false, sh, false.copy()


def portfolio_kwargs(**params):
    return {}
