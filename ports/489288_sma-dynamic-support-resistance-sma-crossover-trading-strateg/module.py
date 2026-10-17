"""SMA 10 / 20 crosses with a breakout and retest filter and a swing bracket, hourly bars: SMA 10 crossing above SMA 20
with the close above the highest SMA 20 of three bars and the last three lows above SMA 20 goes long, stopped at the
10-bar low with a target at twice the risk; the mirror goes short.
Port of FMZ strategy #489288 "动态支撑阻力SMA交叉黄金交易策略三重确认与风险管理优化框架-Dynamic-Support-Resistance-SMA-Crossover-Trading-Strategy-Triple-Confirmation-with-Risk-Management-Optimization-Framework" (Gold Scalping 3M 10-20 SMA).

FMZ source id: 489288

Source
    https://www.fmz.com/strategy/489288 (PineScript v5, FMZ last modified 2025-04-03 10:51:43).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 184-222), SMA 10 / 20, swing 10, RR 2
    buy = crossover(sma10, sma20) and close > highest(sma20, 3) and lowest(low, 3) > sma20;  sell mirrored
    every bar: exit long (stop = lowest(low, 10), limit = close + 2 x (close - stop)); short mirrored with the 10-bar high

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-issued every bar from the current swing and close (a moving level): mark
      trailing_stop_pending. The port fixes it at the signal bar: sl_stop = (close - lowest(low, 10)) / close (shorts
      with the 10-bar high), tp_stop = 2 x that, shifted one bar inside stops(), re-based on the fill. A signal bar
      closing at its own 10-bar extreme (zero risk) emits no entry.
    * Every condition bar is an entry; entries reverse (REVERSAL INTENDED). The title's "Gold 3M" is a label.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket fixed at entry (mark).
    2 generic: PASS, moving averages and swing levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_489288_sma_10_20_cross_retest_swing_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "swing": [10, 20],
    "rr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 20, "swing": 10, "rr": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    s1, s2 = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    buy = (s1 > s2) & (s1.shift(1) <= s2.shift(1)) & (c > s2.rolling(3).max()) & (lo.rolling(3).min() > s2)
    sell = (s1 < s2) & (s1.shift(1) >= s2.shift(1)) & (c < s2.rolling(3).min()) & (h.rolling(3).max() < s2)
    n = int(p["swing"])
    d_long = (c - lo.rolling(n).min()) / c
    d_short = (h.rolling(n).max() - c) / c
    buy = (buy & (d_long > 0)).fillna(False).astype(bool)
    sell = (sell & (d_short > 0)).fillna(False).astype(bool)
    dist = d_long.where(buy, d_short.where(sell))
    return buy, sell, dist


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell, _ = _setup(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, sell, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, dist = _setup(bars_df, p)
    return {"sl_stop": dist.shift(1), "tp_stop": (p["rr"] * dist).shift(1)}


def portfolio_kwargs(**params):
    return {}
