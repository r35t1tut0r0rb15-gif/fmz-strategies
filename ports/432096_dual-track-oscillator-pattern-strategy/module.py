"""EMA 9 against the SMA 20 basis, broker days, long only: the EMA 9 crossing above the SMA 20 goes long; crossing below
closes everything.
Port of FMZ strategy #432096 "Dual track Oscillator Pattern Strategy" (Bollinger Bands Cross EMA).

FMZ source id: 432096

Source
    https://www.fmz.com/strategy/432096 (PineScript v4, FMZ last modified 2023-11-14 14:12:16).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 181-217), SMA 20, EMA 9
    crossover(ema9, sma20) -> entry long;  crossunder(ema9, sma20) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The band lines are commented out; window() is always true. Long only; Opposite entries cannot
      occur. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432096_ema9_sma20_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "ema_len": [9, 5],
}
DEFAULT_PARAMS = {"length": 20, "ema_len": 9}


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
    b = c.rolling(int(p["length"])).mean()
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    up = ((e > b) & (e.shift(1) <= b.shift(1))).astype(bool)
    dn = ((e < b) & (e.shift(1) >= b.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
