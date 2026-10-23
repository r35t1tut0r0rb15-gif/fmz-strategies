"""Four EMAs (13 / 21 / 50 / 180) in order with the ease of movement (SMA 14 of 10000 x change(hl2) x range / volume), broker days, long only: the close above an up-ordered EMA stack with positive ease of movement goes long; a down-ordered stack with negative ease of movement closes.
Port of FMZ strategy #428787 "Four Exponential Moving Averages and Volume Strategy" (4x ema + volume).

FMZ source id: 428787

Source
    https://www.fmz.com/strategy/428787 (PineScript v4, FMZ last modified 2023-10-09 15:05:47).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 124-159), EMA 13 / 21 / 50 / 180; EOM 14, divisor 10000; option1 on, option2 off
    long1 = close > ema1 > ema2 > ema3 > ema4;  short1 = close < ema1 < ema2 < ema3 < ema4;  eom = sma(10000 x change(hl2) x (high - low) / volume, 14)
    long1 and eom > 0 -> entry long;  short1 and eom < 0 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only option1 is on (the crossing variant option2 is off). The ease of movement weights each bar's
      move by 1 / volume, so its sign depends on the volume series. Long only. The 100 % of equity size and
      commission are sizing / costs. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA stack order with an ease-of-movement filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, capital 1000, commission 0.1 % stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the divisor of the ease of movement; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428787_four_ema_stack_ease_of_movement_long"
FAMILY = "ma_stack"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema4l": [180, 100],
    "length": [14, 28],
}
DEFAULT_PARAMS = {"ema4l": 180, "length": 14, "ema1l": 13, "ema2l": 21, "ema3l": 50, "div": 10000}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    e1, e2, e3, e4 = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("ema1l", "ema2l", "ema3l", "ema4l"))
    long1 = (c > e1) & (e1 > e2) & (e2 > e3) & (e3 > e4)
    short1 = (c < e1) & (e1 < e2) & (e2 < e3) & (e3 < e4)
    hl2 = (h + lo) / 2
    eom = (float(p["div"]) * hl2.diff() * (h - lo) / v.where(v != 0)).rolling(int(p["length"])).mean()
    le = long1 & (eom > 0)
    lx = short1 & (eom < 0)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
