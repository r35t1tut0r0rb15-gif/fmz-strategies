"""CDC Action Zone, long only, broker days: the first "green" bar (EMA 12 above EMA 26 of the smoothed price, the price
above the fast line) goes long; the first "red" bar closes everything.
Port of FMZ strategy #429787 "Crossover Master Reversal Breakout Strategy" (CDC Action Zone V.2 strategy).

FMZ source id: 429787

Source
    https://www.fmz.com/strategy/429787 (PineScript v2, FMZ last modified 2023-10-20 17:24:14).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 255-300), EMA 2 of ohlc4, EMA 12 / 26
    AP = ema(ohlc4, 2); Fast = ema(AP, 12); Slow = ema(AP, 26)
    Green = Fast > Slow and AP > Fast; Red = Fast < Slow and AP < Fast
    Green and not Green[1] -> entry long; Red and not Red[1] -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Short / Cover variables are computed but never traded. The date window is dropped.
    * Long only. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average states only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND429787 (2 members, best partner #442211, Jaccard 0.709); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429787_cdc_action_zone_long"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "prd1": [12, 8],
    "prd2": [26, 50],
}
DEFAULT_PARAMS = {"prd1": 12, "prd2": 26}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ap = ((o + h + lo + c) / 4).ewm(span=2, adjust=False).mean()
    f = ap.ewm(span=int(p["prd1"]), adjust=False).mean()
    s = ap.ewm(span=int(p["prd2"]), adjust=False).mean()
    green = (f > s) & (ap > f)
    red = (f < s) & (ap < f)
    long_e = (green & ~green.shift(1, fill_value=False)).astype(bool)
    long_x = (red & ~red.shift(1, fill_value=False)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
