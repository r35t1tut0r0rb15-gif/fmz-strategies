"""SMA 8 / 20 crossings, daily bars: the cross up goes long, the cross down goes short, once the first outside bar of the data has armed the "gap" levels; reversing.
Port of FMZ strategy #458272 "SMA-FVG-SMA交叉策略与公平价值缺口回调结合的综合交易系统Comprehensive-Trading-System-Combining-SMA-Crossover-Strategy-with-Fair-Value-Gap-Pullback" (8 SMA and 20 SMA with FVG Pullback).

FMZ source id: 458272

Source
    https://www.fmz.com/strategy/458272 (PineScript v5, FMZ last modified 2024-07-31 14:38:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 149-195), SMA 8 / 20; fvgHigh / fvgLow set from valuewhen(outside bar, high / low) read as a truth value
    valuewhen(high[1] < high and low[1] > low, high, 0) and valuewhen(..., low, 0) -> fvgHigh = high, fvgLow = low
    crossover(sma8, sma20) and low <= fvgLow -> entry Long;  crossunder and high >= fvgHigh -> entry Short;  crossunder -> close Long;  crossover -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The valuewhen() prices are used as truth values (na before the first outside bar, a non-zero
      price after it), so from the first outside bar on the levels are reset to the current bar's high
      and low on every bar and the pullback tests always hold: the entries are the plain SMA crossings
      from then on, as written. The closes come with the opposite entries that reverse the position
      (#437773). REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458272_sma8_20_cross_after_first_outside_bar_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [8, 5],
    "long_len": [20, 50],
}
DEFAULT_PARAMS = {"short_len": 8, "long_len": 20}


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
    outside = (h.shift(1) < h) & (lo.shift(1) > lo)
    armed = outside.cumsum() > 0             # valuewhen() is na before the first outside bar
    a, b = c.rolling(int(p["short_len"])).mean(), c.rolling(int(p["long_len"])).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1)) & armed
    se = (a < b) & (a.shift(1) >= b.shift(1)) & armed
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
