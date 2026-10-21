"""Noro's weekly and daily ohlc4 levels, 1-hour bars: a bar wholly above both the last completed week's and day's ohlc4 (low above them) on a down candle goes long; a bar wholly below both on an up candle goes short;
reversing.
Port of FMZ strategy #437025 "Multi Timeframe Breakout Strategy" (Levels str 1.1).

FMZ source id: 437025

Source
    https://www.fmz.com/strategy/437025 (PineScript v3, FMZ last modified 2023-12-29 16:18:22).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 113-154), timeframes W and D, source ohlc4, saw filter on, colour filter on; long and short on; date window 1900-2100
    level1 = security(tickerid, "W", ohlc4), level2 = security(tickerid, "D", ohlc4);  up = low > level (saw filter), dn = high < level
    up1 and up2 and close < open -> entry Long;  dn1 and dn2 and close > open -> entry Short (inside the date window)

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-3 security() without lookahead is read as the last completed higher bar (SURVEY_README
      request.security rule): the previous broker day's and the previous broker week's ohlc4 (open of the
      first bar, high, low, close of the last bar of that period), built from the module's own bars; a
      broker week runs Monday to Friday by broker-day label. The date window covers everything: dropped.
      REVERSAL INTENDED. The equity-based lot is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; higher-timeframe values from completed periods.
    2 generic: PASS, levels from the instrument's own completed periods.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity-based lot and capital % stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: previous broker day and broker week (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437025_noro_week_day_levels"
FAMILY = "breakout"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "saw_filter": [True, False],
    "color_filter": [True, False],
}
DEFAULT_PARAMS = {"saw_filter": True, "color_filter": True}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _prev_period_ohlc4(bars_df, key):
    a = bars_df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    per = (a["open"] + a["high"] + a["low"] + a["close"]) / 4
    return per.shift(1).reindex(key).to_numpy()          # the last completed period


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")   # the Monday of the broker week
    lv1 = pd.Series(_prev_period_ohlc4(bars_df, week), index=c.index)
    lv2 = pd.Series(_prev_period_ohlc4(bars_df, day), index=c.index)
    if p["saw_filter"]:
        up1, dn1, up2, dn2 = lo > lv1, h < lv1, lo > lv2, h < lv2
    else:
        up1, dn1, up2, dn2 = c > lv1, c < lv1, c > lv2, c < lv2
    if p["color_filter"]:
        lc = up1 & up2 & (c < o)
        sc = dn1 & dn2 & (c > o)
    else:
        lc = up1 & up2
        sc = dn1 & dn2
    false = pd.Series(False, index=bars_df.index)
    return lc, false, sc, false.copy()


def portfolio_kwargs(**params):
    return {}
