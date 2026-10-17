"""SMA 7 / 10 crosses, long only, 1-hour bars: SMA 7 crossing above SMA 10 goes long; the cross back down closes the trade.
Port of FMZ strategy #486564 "双均线交叉量化交易策略基于短期与中期移动平均线突破系统-Dual-Moving-Average-Crossover-Trading-System-A-Quantitative-Strategy-Based-on-Short-term-and-Medium-term-MA-Breakthrough" (Backtest Buy and Sell Signals with MA 7 and MA 10).

FMZ source id: 486564

Source
    https://www.fmz.com/strategy/486564 (PineScript v5, FMZ last modified 2025-03-14 09:27:34).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 195-219), SMA 7 / 10 (SMA 100 / 200 plotted only)
    crossover(ma7, ma10) -> entry long;  crossunder(ma7, ma10) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SMA 100 / 200 are drawn but unused. The two crosses cannot fall on one bar. Long only: opposite entries
      cannot occur.
    * FREQ = "1h" from the backtest header. No stops. The author's pair (TRUMP_USDT) is the header market only.

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

NAME = "fmz_486564_sma7_10_cross_long_only"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [7, 5],
    "slow": [10, 20],
}
DEFAULT_PARAMS = {"fast": 7, "slow": 10}


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
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    long_x = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
