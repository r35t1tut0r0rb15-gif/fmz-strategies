"""Bollinger (55, 1) band reclaims, broker days, long only: a green candle opening under the lower (or upper) band and closing above it goes long; a candle opening above the upper band and closing under
it, or a close under the lower band, closes.
Port of FMZ strategy #442273 "Bollinger Bands Reversal Strategy" (BB).

FMZ source id: 442273

Source
    https://www.fmz.com/strategy/442273 (PineScript v5, FMZ last modified 2024-02-20 17:05:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 138-174), basis SMA 55 on close; stdev x 1; offset 0 (plots)
    enter = (close > lower and open < lower and close > open) or (close > upper and open < upper and close > open) -> entry Long
    exit = (close < upper and open > upper) or (close > open and upper - lower > 2 basis) or close < lower -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The band-width exit (width above twice the basis) cannot hold for a positive price, as written.
      Pine's stdev is the population deviation. The conditions are levels; an entry while long does
      nothing. Long only. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band reclaim candles.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442273_bb55_band_reclaim_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [55, 20],
    "mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 55, "mult": 1.0}


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
    o, c = bars_df["open"], bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, lo = basis + dev, basis - dev
    green = c > o
    le = ((c > lo) & (o < lo) & green) | ((c > up) & (o < up) & green)
    lx = ((c < up) & (o > up)) | (green & (up - lo > 2 * basis)) | (c < lo)
    false = pd.Series(False, index=c.index)
    return le, lx & ~le, false, false.copy()


def portfolio_kwargs(**params):
    return {}
