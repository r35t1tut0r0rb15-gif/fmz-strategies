"""SMA 7 / 25 crossings on the side of the SMA 99, hourly bars: the up-cross above the SMA 99 goes long, the down-cross below it goes short; reversing (the per-bar ATR bracket is pending).
Port of FMZ strategy #486571 "SMA-ATR动态风险回报比趋势跟踪策略-SMA-ATR-Dynamic-Risk-Reward-Trend-Following-Strategy" (TRH Backtest SMA ATR Variable RR).

FMZ source id: 486571

Source
    https://www.fmz.com/strategy/486571 (PineScript v5, FMZ last modified 2025-03-14 09:45:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 242-282), SMA 7 / 25 / 99; ATR 14 x 1; RR 2 (6 in a local block)
    crossover(sma7, sma25) and close > sma99 -> entry Long;  crossunder(sma7, sma25) and close < sma99 -> entry Short
    every bar: exit(stop = low - atr, limit = close + rr atr) for Long;  mirror for Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.exit is sent on every bar from that bar's low / high and close, so the bracket follows the
      price: not ported, mark trailing_stop_pending (as the C170-C175 readings); the opposite entry is the
      exit. The "riskRewardRatio = 6.0" inside the if block declares a new local variable, so the ratio
      stays 2. An entry on the other side reverses (REVERSAL INTENDED). No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent bracket pending.
    2 generic: PASS, SMA crossings with a long-SMA side filter.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_486571_sma7_25_cross_sma99_side_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [7, 10],
    "slow": [25, 50],
}
DEFAULT_PARAMS = {"fast": 7, "slow": 25, "trend": 99}


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
    t = c.rolling(int(p["trend"])).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (c > t)
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (c < t)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
