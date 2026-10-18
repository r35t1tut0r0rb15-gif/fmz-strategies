"""Crossings of the open-price EMA 11, broker days: the close crossing the EMA of the open with a rising close (this close over the last)
goes long; crossing it with a falling close goes short (reversing).
Port of FMZ strategy #435717 "Galileo Galileis Moving Average Crossover Strategy" (Galileo Galilei).

FMZ source id: 435717

Source
    https://www.fmz.com/strategy/435717 (PineScript v3, FMZ last modified 2023-12-18 12:07:07).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 161-203), EMA 11 of the open
    out = ema(open, 11);  buy: cross(close, out) and close[1] < close -> entry long;  sell: cross(close, out) and close[1] > close -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * cross() is a crossing in either direction; with the rise or fall of the close it is a crossing
      up (long) or down (short) of the line. The date inputs only feed time_cond, which is true:
      dropped. strategy.entry reverses: REVERSAL INTENDED. The cash order size of 100000 is sizing.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the cash order size and capital stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435717_open_ema_close_cross"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [11, 21],
}
DEFAULT_PARAMS = {"length": 11}


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
    out = o.ewm(span=int(p["length"]), adjust=False).mean()
    crossed = ((c > out) & (c.shift(1) <= out.shift(1))) | ((c < out) & (c.shift(1) >= out.shift(1)))
    le = (crossed & (c.shift(1) < c)).fillna(False).astype(bool)
    se = (crossed & (c.shift(1) > c)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
