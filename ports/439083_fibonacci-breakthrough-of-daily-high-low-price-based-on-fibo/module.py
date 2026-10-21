"""Crossings of the first bar's high / low of the day, 10-minute bars, long only: the close crossing over the day's first-bar high buys, crossing under its first-bar low closes.
Port of FMZ strategy #439083 "基于Fibonacci水平的日内高低价突破Breakthrough-of-Daily-High-low-Price-Based-on-Fibonacci-Levels" (DHL Fibonacci).

FMZ source id: 439083

Source
    https://www.fmz.com/strategy/439083 (PineScript v4, FMZ last modified 2024-01-17 15:59:17).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 198-230), day high / low lines and Fibonacci levels shown (plots only)
    change(time("D")) -> dayHigh := high, dayLow := low;  crossover(close, dayHigh) -> entry Buy;  crossunder(close, dayLow) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are set once, on the first bar of each day (they do not follow later highs and lows),
      as written. The day is the broker day (17:00 America/New_York), the house daily session. The
      Fibonacci levels only plot. Long only. No sizing code. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, first-bar day levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the day's first bar.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439083_day_first_bar_level_cross_long"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "exit_on_low": [True, False],
    "buffer": [0.0, 0.001],
}
DEFAULT_PARAMS = {"exit_on_low": True, "buffer": 0.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    day = broker_day(bars_df.index)
    dh = pd.Series(h.groupby(day).transform("first").to_numpy(), index=c.index)
    dl = pd.Series(lo.groupby(day).transform("first").to_numpy(), index=c.index)
    b = float(p["buffer"])
    hi_l, lo_l = dh * (1 + b), (dl if p["exit_on_low"] else dh) * (1 - b)
    up = (c > hi_l) & (c.shift(1) <= hi_l.shift(1))
    dn = (c < lo_l) & (c.shift(1) >= lo_l.shift(1))
    false = pd.Series(False, index=c.index)
    return up, dn & ~up, false, false.copy()


def portfolio_kwargs(**params):
    return {}
