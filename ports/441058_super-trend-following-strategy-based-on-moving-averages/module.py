"""Stacked EMA trend, broker days, long only (the short entry is commented out): from flat, the close above EMA 9 above EMA 21 above EMA 50 above EMA 200 goes long; the close crossing under the EMA 21
closes.
Port of FMZ strategy #441058 "Super Trend Following Strategy Based on Moving Averages" (Super SR).

FMZ source id: 441058

Source
    https://www.fmz.com/strategy/441058 (PineScript v5, FMZ last modified 2024-02-05 11:10:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 132-316), EMA 9 / 21 / 50 / 200 (fixed); RSI 14 computed, unused; NNFX template sections empty
    buy = close > ema9 and ema9 > ema21 and ema21 > ema50 and ema50 > ema200 and position flat -> entry B;  crossunder(close, ema21) -> close B  (the short entry is commented out)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short entry is commented out, so strategy.close("S") never has a position to close. The
      template sections and the RSI are unused. Long only. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stacked EMAs and EMA 21 crossing.
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

NAME = "fmz_441058_stacked_ema_trend_ema21_exit_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len2": [21, 30],
    "len4": [200, 100],
}
DEFAULT_PARAMS = {"len1": 9, "len2": 21, "len3": 50, "len4": 200}


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
    e1, e2, e3, e4 = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("len1", "len2", "len3", "len4"))
    le = (c > e1) & (e1 > e2) & (e2 > e3) & (e3 > e4)
    lx = (c < e2) & (c.shift(1) >= e2.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
