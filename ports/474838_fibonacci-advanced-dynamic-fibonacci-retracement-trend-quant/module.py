"""Closes crossing over the 61.8 % level of the 100-bar range, hourly bars, long only. The exit at the 100-bar high / low, re-sent every bar from the moving extremes, is not ported (pending), so the port has no exit.
Port of FMZ strategy #474838 "高级动态Fibonacci回撤趋势量化交易策略-Advanced-Dynamic-Fibonacci-Retracement-Trend-Quantitative-Trading-Strategy" (Fibonacci Retracement Strategy).

FMZ source id: 474838

Source
    https://www.fmz.com/strategy/474838 (PineScript v5, FMZ last modified 2024-12-12 14:32:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 109-157), lookback 100; levels 0.236 / 0.382 / 0.5 / 0.618 / 0.786 (only 0.618 reaches an order)
    crossover(close, low100 + (high100 - low100) x 0.618) -> entry Buy;  every bar: exit(limit = highest(high, 100), stop = lowest(low, 100))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit levels are the 100-bar extremes of the current bar, re-sent every bar, so they move
      after entry: a level re-set every bar from a moving extreme is not ported (as #438034, mark
      trailing_stop_pending), and the port has no exit. The sell signal and the other levels are
      plotted only. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Fibonacci-level crossings; moving range exit described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_474838_fib618_100bar_range_cross_long_exit_pending"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [100, 50],
    "level": [0.618, 0.5],
}
DEFAULT_PARAMS = {"lookback": 100, "level": 0.618}


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
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["lookback"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    f = ll + (hh - ll) * float(p["level"])
    le = (c > f) & (c.shift(1) <= f.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
