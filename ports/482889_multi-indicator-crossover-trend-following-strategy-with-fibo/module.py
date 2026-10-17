"""EMA 9 / 21 crosses with a 2 % stop / 4 % target, 1-hour bars: EMA 9 crossing above EMA 21 goes long; crossing
below goes short.
Port of FMZ strategy #482889 "多指标交叉趋势跟踪策略结合斐波那契回调及止盈止损优化系统-Multi-Indicator-Crossover-Trend-Following-Strategy-with-Fibonacci-Retracement-and-Stop-Loss-Take-Profit-Optimization-System" (EMA Cross Strategy with TP, SL, Fibonacci Levels, and Trend).

FMZ source id: 482889

Source
    https://www.fmz.com/strategy/482889 (PineScript v5, FMZ last modified 2025-02-20 16:43:42).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 106-166), EMA 9 / 21, SL 2 %, TP 4 %
    long = crossover(ema9, ema21): entry + exit(stop = close x 0.98, limit = close x 1.04) (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal close: 2 % / 4 % re-based on the fill (house rule). Crosses
      alternate, so no re-placement. The Fibonacci levels and trend label only feed plots.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar.
    2 generic: PASS, moving averages and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_482889_ema9_21_cross_pct_bracket_2_4"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [2.0, 1.0],
    "tp_pct": [4.0, 6.0],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "sl_pct": 2.0, "tp_pct": 4.0}


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
    short_e = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
