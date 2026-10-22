"""EMA 14 candle breaks, daily bars, long only and with no exit: a green candle crossing over the EMA 14 with at least half its body above it and wicks at most 40 % of its range buys, and the position is held.
Port of FMZ strategy #475630 "EMA交叉与蜡烛体穿透结合动态买入策略-Dynamic-Buy-Entry-Strategy-Combining-EMA-Crossing-and-Candle-Body-Penetration" (Buy Entry with EMA Crossing and Wick Conditions).

FMZ source id: 475630

Source
    https://www.fmz.com/strategy/475630 (PineScript v5, FMZ last modified 2024-12-20 16:50:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 103-144), EMA 14; body >= 50 % over the EMA; wicks <= 40 %
    green and crossover(close, ema14) and (close - open) x 0.5 <= close - ema14 and wicks / range <= 0.4 -> entry Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no exit: the first signal's long is held to the end of the data (as #451391, a
      port with no exit). The same buy rule as #475606 without its sell side. Long only. No sizing
      code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA candle breaks; no exit, as written.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_475630_ema14_candle_break_body_wick_long_no_exit"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [14, 21],
}
DEFAULT_PARAMS = {"ema_length": 14}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    wick = ((h - c) + (o - lo)) / (h - lo)
    le = (c > o) & (c > e) & (c.shift(1) <= e.shift(1)) & ((c - o) * 0.5 <= c - e) & (wick <= 0.4)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
