"""Chikou-span test against displaced Tenkan / Kijun, broker days, long only: the close 26 bars ago over the Tenkan and the Kijun of 26 bars
ago (both lines evaluated 26 bars back) goes long; under both closes the long.
Port of FMZ strategy #435699 "Trend Following Strategy Based on Ichimoku Cloud" (My Custom Strategy).

FMZ source id: 435699

Source
    https://www.fmz.com/strategy/435699 (PineScript v5, FMZ last modified 2023-12-18 10:20:01).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 106-128), Tenkan 9, Kijun 26, displacement 26
    chikouSpan = close[26];  buy = chikouSpan > tenkanSen[26] and chikouSpan > kijunSen[26];  sell = chikouSpan < tenkanSen[26] and chikouSpan < kijunSen[26]
    buy -> entry long;  sell -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every term is shifted 26 bars, so the rule is the plain "close over Tenkan and Kijun" test of 26
      bars ago, acted on today: as written (a 26-bar delayed signal). Long only. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku lines.
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

NAME = "fmz_435699_chikou_displaced_lines_long"
FAMILY = "ichimoku"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tenkan": [9, 7],
    "kijun": [26, 22],
}
DEFAULT_PARAMS = {"tenkan": 9, "kijun": 26, "displacement": 26}


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
    d = int(p["displacement"])
    tenkan = (h.rolling(int(p["tenkan"])).max() + lo.rolling(int(p["tenkan"])).min()) / 2
    kijun = (h.rolling(int(p["kijun"])).max() + lo.rolling(int(p["kijun"])).min()) / 2
    chikou = c.shift(d)
    buy = ((chikou > tenkan.shift(d)) & (chikou > kijun.shift(d))).fillna(False).astype(bool)
    sell = ((chikou < tenkan.shift(d)) & (chikou < kijun.shift(d))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return buy, sell, false, false.copy()


def portfolio_kwargs(**params):
    return {}
