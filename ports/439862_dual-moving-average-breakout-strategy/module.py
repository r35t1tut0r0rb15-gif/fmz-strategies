"""CDC Action Zone, long only, broker days: on ohlc4 smoothed by an EMA 2, the EMA 12 turning above the EMA 26 goes long, turning below closes.
Port of FMZ strategy #439862 "Dual Moving Average Breakout Strategy" (CDC Action Zone V.2).

FMZ source id: 439862

Source
    https://www.fmz.com/strategy/439862 (PineScript v4, FMZ last modified 2024-01-24 14:49:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 163-227), long only; source ohlc4; EMA 2, then 12 / 26; date window true
    AP = ema(ohlc4, 2);  Fast = ema(AP, 12);  Slow = ema(AP, 26);  Buy = Fast > Slow and Fast[1] < Slow[1] -> entry L;  Sell = Fast < Slow and Fast[1] > Slow[1] -> close L

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long-only branch of the script; Buy and Sell cannot share a bar. Long only. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings of smoothed ohlc4.
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

NAME = "fmz_439862_cdc_action_zone_v2_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
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
    buy = (f > s) & (f.shift(1) < s.shift(1))
    sell = (f < s) & (f.shift(1) > s.shift(1))
    false = pd.Series(False, index=c.index)
    return buy, sell, false, false.copy()


def portfolio_kwargs(**params):
    return {}
