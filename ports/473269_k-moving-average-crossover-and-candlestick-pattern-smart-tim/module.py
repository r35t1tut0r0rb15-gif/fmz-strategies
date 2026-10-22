"""SMA 14 / 28 crossings, hourly bars: the cross up goes long, the cross down goes short; reversing. The wick-reversal signals above the strategy are only computed (the indicator declaration is commented out) and never reach an order.
Port of FMZ strategy #473269 "均线交叉趋势捕捉与K线突破智能择时策略-Moving-Average-Crossover-and-Candlestick-Pattern-Smart-Timing-Strategy" (My strategy).

FMZ source id: 473269

Source
    https://www.fmz.com/strategy/473269 (PineScript v5, FMZ last modified 2024-11-28 17:18:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-132), wick multiplier 3.5, body share 0.25 (computed only); SMA 14 / 28 (constants)
    crossover(sma14, sma28) -> entry L;  crossunder(sma14, sma28) -> entry S

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "//@version=5 indicator(...)" line is a comment, so the script is the strategy below it; the
      wick signals are not plotted into orders. There is no exit: positions end at the opposite entry.
      REVERSAL INTENDED. Margin settings only, no sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: margin settings only.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473269_sma14_28_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    c = bars_df["close"]
    a, b = c.rolling(14).mean(), c.rolling(28).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
