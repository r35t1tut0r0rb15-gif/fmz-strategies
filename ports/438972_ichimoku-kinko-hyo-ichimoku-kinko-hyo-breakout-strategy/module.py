"""Ichimoku breakouts above the displaced cloud, broker days, long only: Tenkan 7 above Kijun 14, a positive 13-bar momentum and the close above the cloud of 13 bars ago buys; the bearish mirror closes.
Port of FMZ strategy #438972 "基于Ichimoku-Kinko-Hyo指标的突破策略Ichimoku-Kinko-Hyo-Breakout-Strategy" (Ichimoku Kinko Hyo: Basic Strategy).

FMZ source id: 438972

Source
    https://www.fmz.com/strategy/438972 (PineScript v5, FMZ last modified 2024-01-16 17:12:49).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 150-193), Tenkan 7, Kijun 14, Senkou B 28; Chikou offset 14, Senkou offset 14; long entry on, short entry off
    bullish = tenkan > kijun and mom(close, 13) > 0 and close > max(senkouA[13], senkouB[13]);  bearish = mirror under min(...)
    bullish -> entry Long;  bearish and not short_entry -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cloud is the spans of 13 bars ago (displacement - 1), all from completed bars. Short entries are
      off, so the bearish setup only closes the long. Long only. No sizing code. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku lines and displaced cloud.
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

NAME = "fmz_438972_ichimoku_cloud_breakout_long"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ts_bars": [7, 9],
    "ks_bars": [14, 26],
}
DEFAULT_PARAMS = {"ts_bars": 7, "ks_bars": 14, "ssb_bars": 28, "cs_offset": 14, "ss_offset": 14}


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


def _mid(h, lo, n):
    return (lo.rolling(n).min() + h.rolling(n).max()) / 2


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    tenkan = _mid(h, lo, int(p["ts_bars"]))
    kijun = _mid(h, lo, int(p["ks_bars"]))
    sa = (tenkan + kijun) / 2
    sb = _mid(h, lo, int(p["ssb_bars"]))
    k = int(p["ss_offset"]) - 1
    ss_high = np.maximum(sa.shift(k), sb.shift(k))
    ss_low = np.minimum(sa.shift(k), sb.shift(k))
    mom = c - c.shift(int(p["cs_offset"]) - 1)
    bull = (tenkan > kijun) & (mom > 0) & (c > ss_high)
    bear = (tenkan < kijun) & (mom < 0) & (c < ss_low)
    false = pd.Series(False, index=c.index)
    return bull, bear, false, false.copy()


def portfolio_kwargs(**params):
    return {}
