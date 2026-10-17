"""EMA 9 / 21 and MACD crossing up on the same bar, long only, closed when either crosses down, signals suppressed on
the first bar of each UTC day, 1-hour bars.
Port of FMZ strategy #483047 "多周期均线带及MACD交叉策略系统-Multi-Period-Moving-Average-Ribbon-and-MACD-Crossover-Strategy-System" (Daily MA Ribbon + MACD Crossover with Buy/Sell Signals).

FMZ source id: 483047

Source
    https://www.fmz.com/strategy/483047 (PineScript v6, FMZ last modified 2025-02-21 10:51:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 89-166), MA 1 EMA 9, MA 2 EMA 21, MACD 12 / 26 / 9 (EMA / EMA)
    buy = crossover(ma1, ma2) and crossover(macd, signal); sell = crossunder(ma1, ma2) or crossunder(macd, signal)
    newDay = change(time("D")) -> both false; buy -> entry long; sell -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Clock rule (C6): time("D") is the chart's exchange day, 00:00 UTC on the author's Binance chart (as #491506);
      on the first bar of each UTC day no signal is taken, as written (the very first bar counts as a change).
    * The MA types default to EMA (the VWMA option is not used: no volume). Long only; the source has no shorts.
      No stops. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages and MACD.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: day boundary 00:00 UTC (the author's exchange day) suppresses that bar's signals; no venue-open rule.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483047_ema9_21_macd_joint_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1_len": [9, 12],
    "ma2_len": [21, 26],
}
DEFAULT_PARAMS = {"ma1_len": 9, "ma2_len": 21, "fast": 12, "slow": 26, "signal": 9}


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
    m1 = c.ewm(span=int(p["ma1_len"]), adjust=False).mean()
    m2 = c.ewm(span=int(p["ma2_len"]), adjust=False).mean()
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    day = bars_df.index.tz_convert("UTC").normalize()
    new_day = pd.Series(np.concatenate(([True], day[1:] != day[:-1])), index=c.index)
    buy = (m1 > m2) & (m1.shift(1) <= m2.shift(1)) & (macd > sig) & (macd.shift(1) <= sig.shift(1))
    sell = ((m1 < m2) & (m1.shift(1) >= m2.shift(1))) | ((macd < sig) & (macd.shift(1) >= sig.shift(1)))
    false = pd.Series(False, index=bars_df.index)
    return (buy & ~new_day).astype(bool), (sell & ~new_day).astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
