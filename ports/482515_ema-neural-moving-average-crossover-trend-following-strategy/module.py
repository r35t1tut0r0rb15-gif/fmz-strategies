"""EMA 200 side after SMA 9 / 15 crossings, hourly bars: once an up-crossing has occurred, any close above the EMA 200 holds a long; once a down-crossing has occurred, any close below it holds a short; a crossing closes the other side when the close sits exactly on the EMA; reversing.
Port of FMZ strategy #482515 "神经均线交叉趋势跟踪策略结合EMA过滤系统-Neural-Moving-Average-Crossover-Trend-Following-Strategy-with-EMA-Filtering-System" (SMA Crossover with EMA Filter).

FMZ source id: 482515

Source
    https://www.fmz.com/strategy/482515 (PineScript v5, FMZ last modified 2025-02-18 18:29:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 135-180), SMA 9 / 15; EMA 200
    crossover(sma9, sma15) and close > ema200 -> entry Buy;  crossunder and close < ema200 -> entry Sell;  crossunder -> close Buy;  crossover -> close Sell
    barssince(crossover) > 0 and close > ema200 -> entry Buy;  barssince(crossunder) > 0 and close < ema200 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The re-entries fire on every bar after the first crossing of their kind while the close is on their
      side of the EMA 200, so the position follows the EMA side; a crossing's close followed by the same
      side's re-entry on one bar keeps the position here (the source closes and reopens it at the same
      open). The closes act alone only when the close equals the EMA. REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA 200 side after SMA crossings.
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

NAME = "fmz_482515_ema200_side_after_sma9_15_cross_reentry_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [200, 100],
    "sma_fast": [9, 5],
}
DEFAULT_PARAMS = {"ema_length": 200, "sma_fast": 9, "sma_slow": 15}


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
    f, s = c.rolling(int(p["sma_fast"])).mean(), c.rolling(int(p["sma_slow"])).mean()
    ema = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    bull = (f > s) & (f.shift(1) <= s.shift(1))
    bear = (f < s) & (f.shift(1) >= s.shift(1))
    bull_seen = pd.Series(np.maximum.accumulate(bull.to_numpy()), index=c.index)
    bear_seen = pd.Series(np.maximum.accumulate(bear.to_numpy()), index=c.index)
    le = (c > ema) & bull_seen
    se = (c < ema) & bear_seen
    return le, bear & ~le & ~se, se, bull & ~le & ~se


def portfolio_kwargs(**params):
    return {}
