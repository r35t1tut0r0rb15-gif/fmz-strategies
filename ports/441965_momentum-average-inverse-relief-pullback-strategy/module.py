"""Engulfing candles crossing the EMA 50, broker days: a bullish engulfing candle closing up through the EMA 50 goes long, a bearish engulfing candle closing down through it goes short; reversing.
Port of FMZ strategy #441965 "Momentum Average Inverse Relief Pullback Strategy" (EPS).

FMZ source id: 441965

Source
    https://www.fmz.com/strategy/441965 (PineScript v5, FMZ last modified 2024-02-18 10:21:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 173-207), EMA 50; "1-minute" timer exit on id "Exit"
    long = crossover(close, ema50) and bullish engulfing -> entry Buy;  short = crossunder(close, ema50) and bearish engulfing -> entry Sell;  timer >= 1 -> strategy.close("Exit")

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.close("Exit") names an id no entry has, so it never closes anything; positions end only
      at the opposite entry. strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, engulfing candles and EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441965_engulfing_ema50_cross_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_period": [50, 100],
}
DEFAULT_PARAMS = {"ema_period": 50}


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
    o, c = bars_df["open"], bars_df["close"]
    e = c.ewm(span=int(p["ema_period"]), adjust=False).mean()
    o1, c1 = o.shift(1), c.shift(1)
    bull = (c1 < o1) & (c > o) & (c > c1) & (o < o1)
    bear = (c1 > o1) & (o > c) & (o > o1) & (c < c1)
    up = (c > e) & (c1 <= e.shift(1)) & bull
    dn = (c < e) & (c1 >= e.shift(1)) & bear
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
