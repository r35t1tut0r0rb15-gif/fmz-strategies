"""Double-EMA spread, long only, broker days: with the EMA of the EMA 10 above the EMA of the EMA 21 and their spread above
+0.05 % of their mean, the strategy goes long; with it below and the spread under -0.165 %, it closes the long.
Port of FMZ strategy #432763 "基于双EMA交叉的量化交易策略Quantitative-Trading-Strategy-Based-on-Double-EMA-Crossover" (ema(ema10-21)).

FMZ source id: 432763

Source
    https://www.fmz.com/strategy/432763 (PineScript v3, FMZ last modified 2023-11-21 11:41:40).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 125-152), double EMA 10 / 21, thresholds +0.05 % / -0.165 %
    short = ema(ema(close, 10), 10); long = ema(ema(close, 21), 21); growth = (short - long) x 100 / ((short + long) / 2)
    short > long and growth > 0.05 -> entry long;  short < long and growth < -0.165 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The thresholds are percentages of the averages' mean, scale-free as written. The start-time
      limiter is off (startTimeOk is always true). Long only; Opposite entries cannot occur. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a percentage spread of two smoothed EMAs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the commission stored in original_sizing.txt.
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

NAME = "fmz_432763_double_ema_spread_long"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len0": [10, 5],
    "len1": [21, 42],
}
DEFAULT_PARAMS = {"len0": 10, "len1": 21, "th_up": 0.05, "th_dn": -0.165}


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
    a, b = int(p["len0"]), int(p["len1"])
    s = c.ewm(span=a, adjust=False).mean().ewm(span=a, adjust=False).mean()
    lg = c.ewm(span=b, adjust=False).mean().ewm(span=b, adjust=False).mean()
    g = (s - lg) * 100 / ((s + lg) / 2)
    le = ((s > lg) & (g > float(p["th_up"]))).astype(bool)
    lx = ((s < lg) & (g < float(p["th_dn"]))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
