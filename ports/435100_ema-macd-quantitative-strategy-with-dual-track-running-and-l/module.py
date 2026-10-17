"""EMA 25 / 50 crosses on the MACD's side of zero, broker days: the EMA 25 crossing above the EMA 50 with the MACD 12 / 26
above zero goes long, the cross down with the MACD below zero goes short (reversing).
Port of FMZ strategy #435100 "EMA MACD Quantitative Strategy With Dual Track Running and Leading the Market Index" (EMA+MACD).

FMZ source id: 435100

Source
    https://www.fmz.com/strategy/435100 (PineScript v4, FMZ last modified 2023-12-12 12:13:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 176-204), MACD 12 / 26 / 9 (EMA); EMA 25 / 50
    crossover(ema25, ema50) and macd > 0 -> entry long;  crossover(ema50, ema25) and macd < 0 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The labels are drawing only. strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crosses and a MACD sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_435100_ema_cross_macd_sign"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [25, 10],
    "len2": [50, 100],
}
DEFAULT_PARAMS = {"len1": 25, "len2": 50, "fast": 12, "slow": 26}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    e1 = c.ewm(span=int(p["len1"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["len2"]), adjust=False).mean()
    le = ((e1 > e2) & (e1.shift(1) <= e2.shift(1)) & (macd > 0)).astype(bool)
    se = ((e2 > e1) & (e2.shift(1) <= e1.shift(1)) & (macd < 0)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
