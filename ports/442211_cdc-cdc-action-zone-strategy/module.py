"""CDC Action Zone colours, broker days: the first green bar (EMA 12 of the 2-bar EMA of ohlc4 above its EMA 26, with that average above the fast line) goes long, the first red bar goes short; reversing.
Port of FMZ strategy #442211 "CDC动作区域策略CDC-Action-Zone-Strategy" (CDC Action Zone [TS Trader]).

FMZ source id: 442211

Source
    https://www.fmz.com/strategy/442211 (PineScript v4, FMZ last modified 2024-02-20 11:23:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 136-190), source ohlc4; AP = ema(src, 2); fast 12, slow 26; dates 2019-9999 (window() true)
    Green = Fast > Slow and AP > Fast;  Red = Fast < Slow and AP < Fast;  Buy = Green and not Green[1] -> entry Buy, close Sell;  Sell = Red and not Red[1] -> entry Sell, close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each close goes with the opposite entry, one reversal. strategy.entry reverses: REVERSAL INTENDED.
      No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Action Zone colour changes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND429787 (2 members, best partner #429787, Jaccard 0.709); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442211_cdc_action_zone_colour_reversal"
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
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    ap = ((o + h + lo + c) / 4).ewm(span=2, adjust=False).mean()
    fast = ap.ewm(span=int(p["prd1"]), adjust=False).mean()
    slow = ap.ewm(span=int(p["prd2"]), adjust=False).mean()
    green = (fast > slow) & (ap > fast)
    red = (fast < slow) & (ap < fast)
    buy = green & ~green.shift(1, fill_value=False)
    sell = red & ~red.shift(1, fill_value=False)
    false = pd.Series(False, index=c.index)
    return buy, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
