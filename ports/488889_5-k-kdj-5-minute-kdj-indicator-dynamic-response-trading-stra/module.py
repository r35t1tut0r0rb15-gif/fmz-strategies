"""Stochastic %K 5 (unsmoothed) extremes, broker days: K under 5 goes long and K over 90 closes it; K over 95 goes short and K under 10 closes it; reversing.
Port of FMZ strategy #488889 "5分钟K线KDJ指标动态响应交易策略-5-Minute-KDJ-Indicator-Dynamic-Response-Trading-Strategy" (Demo GPT - KDJ Strategy).

FMZ source id: 488889

Source
    https://www.fmz.com/strategy/488889 (PineScript v6, FMZ last modified 2025-03-31 16:26:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 195-237), stoch length 5, smooth K 1, smooth D 1; long < 5 / exit > 90; short > 95 / exit < 10; slippage 3 ticks
    k < 5 -> entry Long (qty = floor(equity / close));  k > 90 -> close Long;  k > 95 -> entry Short;  k < 10 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * With smoothing 1, K is the raw 5-bar stochastic (na when the range is zero). The conditions are
      states; an opposite entry would reverse (REVERSAL INTENDED). The whole-equity quantity and slippage
      are sizing and costs. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic extremes as entries and exits.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: equity-sized quantity and slippage stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488889_stoch5_k_extremes_entries_exits_reversal"
FAMILY = "stochastic"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [5, 14],
    "long_entry": [5, 20],
}
DEFAULT_PARAMS = {"length": 5, "long_entry": 5, "long_exit": 90, "short_exit": 10}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = 100 * (c - ll) / (hh - ll).where(hh > ll)
    le = k < float(p["long_entry"])
    se = k > 100 - float(p["long_entry"])
    lx = (k > float(p["long_exit"])) & ~se
    sx = (k < float(p["short_exit"])) & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
