"""Noro price-channel bands, broker days: the trend turns up when the close is above the upper distance band (and the low above the lower), down on the mirror; in an uptrend a red candle or a close under
the upper band goes long, in a downtrend a green candle or a close over the lower band goes short; reversing.
Port of FMZ strategy #441138 "基于Price-Channel和均线的趋势跟踪策略Price-Channel-and-Moving-Average-Based-Trend-Following-Strategy" (NoroBands str 1.1).

FMZ source id: 441138

Source
    https://www.fmz.com/strategy/441138 (PineScript v2, FMZ last modified 2024-02-06 09:46:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 134-180), long and short on; period 20; color on; bands and background display only
    center = (highest(close, 20) + lowest(close, 20)) / 2;  distsma = sma(|close - center|, 20);  hd = center + distsma, ld = center - distsma
    trend = close < ld and high < hd ? -1 : close > hd and low > ld ? 1 : trend[1];  up = trend == 1 and (close < open or close < hd) -> entry Long;  dn = trend == -1 and (close > open or close > ld) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * With color on the candle test is used as written. trend keeps its previous value between the tests
      (na until the first). The entries are levels; an entry while already in that direction does nothing.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price-channel distance bands and candle colours.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: ND441138 (2 members, best partner #442523, Jaccard 0.697); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441138_noro_channel_distance_bands_reversal"
FAMILY = "trend_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
}
DEFAULT_PARAMS = {"length": 20}


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
    n = int(p["length"])
    center = (c.rolling(n).max() + c.rolling(n).min()) / 2
    ds = (c - center).abs().rolling(n).mean()
    hd, ld = center + ds, center - ds
    dn_t = ((c < ld) & (h < hd)).to_numpy()
    up_t = ((c > hd) & (lo > ld)).to_numpy()
    m = len(c)
    trend = np.full(m, np.nan)
    t = np.nan
    for i in range(m):
        if dn_t[i]:
            t = -1.0
        elif up_t[i]:
            t = 1.0
        trend[i] = t
    tr = pd.Series(trend, index=c.index)
    le = (tr == 1) & ((c < o) | (c < hd))
    se = (tr == -1) & ((c > o) | (c > ld))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
