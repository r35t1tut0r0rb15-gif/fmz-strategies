"""SMA 10 / 20 crossings with a break of the 3-bar SMA 20 extreme and the 3-bar low (high) on the right side of the SMA 20, hourly bars: the confirmed up-cross goes long, the confirmed down-cross goes short; reversing (the per-bar swing bracket is pending).
Port of FMZ strategy #489288 "动态支撑阻力SMA交叉黄金交易策略三重确认与风险管理优化框架-Dynamic-Support-Resistance-SMA-Crossover-Trading-Strategy-Triple-Confirmation-with-Risk-Management-Optimization-Framework" (Gold Scalping 3M 10-20 SMA).

FMZ source id: 489288

Source
    https://www.fmz.com/strategy/489288 (PineScript v5, FMZ last modified 2025-04-03 10:51:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 176-223), SMA 10 / 20; swing 10; RR 2; 1 % of equity
    crossover(sma10, sma20) and close > highest(sma20, 3) and lowest(low, 3) > sma20 -> entry Long;  mirror -> entry Short
    every bar: exit(stop = lowest(low, 10), limit = close + 2 (close - lowest(low, 10))) for Long;  mirror for Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.exit is sent on every bar from that bar's 10-bar low / high and close, so the bracket
      follows the price: not ported, mark trailing_stop_pending (as the C170-C175 readings); the opposite
      entry is the exit. An entry on the other side reverses (REVERSAL INTENDED). MPL 2.0 source (the notice
      is kept: Mozilla Public License 2.0, © DoubleuEdge). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent bracket pending.
    2 generic: PASS, SMA crossings with breakout and retest filters.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 1 % of equity stored, not ported.
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

NAME = "fmz_489288_sma10_20_cross_breakout_retest_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 5],
    "slow": [20, 50],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 20}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    le = ((f > s) & (f.shift(1) <= s.shift(1)) & (c > s.rolling(3).max()) & (lo.rolling(3).min() > s))
    se = ((f < s) & (f.shift(1) >= s.shift(1)) & (c < s.rolling(3).min()) & (h.rolling(3).max() < s))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
