"""Broker days: the 5-bar sum of (close - open) x volume crossing UNDER its 5-bar SMA goes long, crossing over it goes short (the script's "bullish" cross opens the short, as written); the opposite signal reverses.
Port of FMZ strategy #474711 "Volume Weighted Dual Trend Detection System" (Volume-Weighted Delta Strategy).

FMZ source id: 474711

Source
    https://www.fmz.com/strategy/474711 (PineScript v5, FMZ last modified 2024-12-11 17:41:23).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 108-158), delta = sum over 5 bars of (close - open) x volume; SMA 5 of it; volume threshold input unused
    BullishCond = crossover(ma_value, delta_value) -> entry Sell (short);  BearishCond = crossunder(ma_value, delta_value) -> entry Buy (long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The names are inverted in the script: the SMA crossing over the delta (falling volume-weighted
      bodies) opens a SHORT and the SMA crossing under it opens a LONG; ported as written (weird case).
      The 100000 volume-threshold input is never used. Entries only; an opposite entry reverses.
      REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume-weighted candle-body delta crossings of its average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) weighting the candle bodies; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474711_volume_weighted_body_delta_cross_reversal"
FAMILY = "volume_delta"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "delta_len": [5, 10],
    "ma_len": [5, 10],
}
DEFAULT_PARAMS = {"delta_len": 5, "ma_len": 5}


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
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    delta = ((c - o) * v).rolling(int(p["delta_len"])).sum()
    ma = delta.rolling(int(p["ma_len"])).mean()
    sell = (ma > delta) & (ma.shift(1) <= delta.shift(1))      # "BullishCond" -> short
    buy = (ma < delta) & (ma.shift(1) >= delta.shift(1))       # "BearishCond" -> long
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
