"""Pullbacks in an EMA 10 / 30 trend with CCI extremes, 1-hour bars: with the fast EMA over the slow, a green bar after a close under the fast EMA and a CCI 20 under -100 goes long; the mirror goes short; reversing.
Port of FMZ strategy #452359 "CCI双均线交叉回撤买入策略-CCI-MA-Crossover-Pullback-Buy-Strategy" (CCI + MA Crossover Pullback Buy Strategy [TradeDots]).

FMZ source id: 452359

Source
    https://www.fmz.com/strategy/452359 (PineScript v5, FMZ last modified 2024-05-24 17:45:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-159), EMA 10 / 30 of close[1]; CCI 20 of hlc3 (EMA of hlc3[1] as its average), threshold 100
    fast > slow and close[1] < fast and close > open and cci < -100 -> entry Long;  fast < slow and close[1] > fast and close < open and cci > 100 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source's ma() helper averages source[1], so both EMAs and the CCI's own average lag the
      bar by one, as written; the CCI divides by ta.dev (the mean absolute deviation of hlc3 around
      its SMA 20). The two entries cannot meet on one bar. There is no exit: positions end at the
      opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, trend pullbacks with CCI extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_452359_ema10_30_pullback_cci_extreme_reversal"
FAMILY = "ma_pullback"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 20],
    "slow": [30, 50],
    "cci_len": [20, 14],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 30, "cci_len": 20, "threshold": 100.0}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    hlc3 = (h + lo + c) / 3
    n = int(p["cci_len"])
    cci_ma = hlc3.shift(1).ewm(span=n, adjust=False).mean()
    mad = hlc3.rolling(n).apply(lambda v: np.abs(v - v.mean()).mean(), raw=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        cci = (hlc3 - cci_ma) / (0.015 * mad)
    fast = c.shift(1).ewm(span=int(p["fast"]), adjust=False).mean()
    slow = c.shift(1).ewm(span=int(p["slow"]), adjust=False).mean()
    t = float(p["threshold"])
    c1 = c.shift(1)
    le = (fast > slow) & (c1 < fast) & (c > o) & (cci < -t)
    se = (fast < slow) & (c1 > fast) & (c < o) & (cci > t)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
