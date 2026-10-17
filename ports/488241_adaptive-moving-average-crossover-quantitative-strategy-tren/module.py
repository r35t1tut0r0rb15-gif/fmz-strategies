"""Moving-average 9 / 21 crosses, long only, 2-hour bars: the fast MA crossing above the slow MA goes long; the cross
back down closes the trade.
Port of FMZ strategy #488241 "多均线交叉量化策略系统基于自适应移动平均线的趋势跟踪与交易信号优化-Adaptive-Moving-Average-Crossover-Quantitative-Strategy-Trend-Following-and-Trading-Signal-Optimization" (Moving Average Crossover Strategy).

FMZ source id: 488241

Source
    https://www.fmz.com/strategy/488241 (PineScript v5, FMZ last modified 2025-03-26 11:09:45).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 199-227), fast 9, slow 21, MA type SMA
    crossover(fastMA, slowMA) -> entry long;  crossunder(fastMA, slowMA) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The MA-type input is a GRID variant (SMA, the default, and EMA); the VWMA option uses volume and is not offered
      (check 8); WMA is not in the grid.
    * The two crosses cannot fall on one bar. Long only: opposite entries cannot occur.
    * FREQ = "2h" from the backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488241_ma9_21_cross_long_only"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_type": ["SMA", "EMA"],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "ma_type": "SMA"}


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


def _ma(x, n, kind):
    if kind == "EMA":
        return x.ewm(span=n, adjust=False).mean()
    return x.rolling(n).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = _ma(c, int(p["fast"]), p["ma_type"]), _ma(c, int(p["slow"]), p["ma_type"])
    long_e = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    long_x = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
