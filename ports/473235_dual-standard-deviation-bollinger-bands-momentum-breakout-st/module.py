"""Closes beyond the Bollinger 34 / 2 bands, daily bars: a close over the upper band holds long, a close under the lower band holds short; reversing.
Port of FMZ strategy #473235 "Dual Standard Deviation Bollinger Bands Momentum Breakout Strategy" (Baker Odeh's Strategy - Bollinger Bands).

FMZ source id: 473235

Source
    https://www.fmz.com/strategy/473235 (PineScript v5, FMZ last modified 2024-11-28 15:10:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-143), SMA 34, sd 34 (population); 1 and 2 sd bands (the 1 sd only plotted); 20 % of equity, capital 30
    close > upper2 -> entry Long;  close < lower2 -> entry Short;  close <= lower2 -> close Long;  close >= upper2 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes come with the reversing entries (#437773). The tests are states: repeated entries
      while held do nothing. The equity share is not ported. REVERSAL INTENDED. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band breakouts held as states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND455366 (2 members, best partner #455366, Jaccard 0.779); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473235_bb34_2sd_close_beyond_band_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [34, 20],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 34, "mult": 2.0}


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
    false = pd.Series(False, index=bars_df.index)
    return c > basis + dev, false, c < basis - dev, false.copy()


def portfolio_kwargs(**params):
    return {}
