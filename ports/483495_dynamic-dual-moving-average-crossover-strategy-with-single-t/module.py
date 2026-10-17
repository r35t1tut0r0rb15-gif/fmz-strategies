"""EMA 9 / 21 crosses, one long trade at a time, 1-hour bars: EMA 9 crossing above EMA 21 from flat goes long;
crossing below closes it.
Port of FMZ strategy #483495 "双均线动态交叉策略之指数移动均线交叉执行单次交易系统-Dynamic-Dual-Moving-Average-Crossover-Strategy-with-Single-Trade-Execution-System-using-Exponential-Moving-Averages" (EMA Crossover Labels (One Trade at a Time)).

FMZ source id: 483495

Source
    https://www.fmz.com/strategy/483495 (PineScript v6, FMZ last modified 2025-02-24 09:15:19).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 95-122), EMA 9 / 21
    buy = crossover(ema9, ema21) and position_size == 0 -> entry long
    sell = crossunder(ema9, ema21) and position_size > 0 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "Strategy Timeframe" input (10) is never used: the chart's bars, FREQ = "1h" from the backtest header.
    * Long only; a cross up while held is ignored and a cross down while flat does nothing, so the raw crosses are
      emitted (the engine ignores them alike). No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483495_ema9_21_cross_long_only"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 12],
    "slow": [21, 26],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    long_x = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
