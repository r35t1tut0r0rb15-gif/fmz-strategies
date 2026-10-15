"""Ujanja: a Hull-style smoothing (WMA lengths 88 / 176 / 13) of a zero-lag EMA 30; while the
smoothing is above its value from the previous bar's inputs the strategy is long, otherwise short
(always in the market).
Port of FMZ strategy #427274 "Zero-Lag Hull EMA Combo Trend Following Strategy".

FMZ source id: 427274

Source
    https://www.fmz.com/strategy/427274 (PineScript v3, FMZ last modified 2023-09-19 16:53:31).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 170-206), period 30, smoother 176
    zl = 2 ema(close, 30) - ema(ema(close, 30), 30)
    n1 = wma(2 wma(zl, 88) - wma(zl, 176), 13); n2 = the same of zl[1]
    n1 > n2 -> entry long; otherwise -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * round(176 / 2) = 88, round(sqrt(176)) = 13; wma weights 1..n, the current bar heaviest.
    * `shortCondition = longCondition != true` is also true while n1 / n2 are not yet defined
      (na > na is false), so the script is short from its first bar; ported as written.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427274_ujanja_zero_lag_hull"
FAMILY = "ma_trend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [30, 15, 60],
    "s_period": [176, 88],
}
DEFAULT_PARAMS = {"period": 30, "s_period": 176}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n, s = int(p["period"]), int(p["s_period"])
    c = bars_df["close"]
    e1 = c.ewm(span=n, adjust=False).mean()
    zl = 2 * e1 - e1.ewm(span=n, adjust=False).mean()
    half, sq = int(round(s / 2)), int(round(np.sqrt(s)))
    n1 = _wma(2 * _wma(zl, half) - _wma(zl, s), sq)
    zl1 = zl.shift(1)
    n2 = _wma(2 * _wma(zl1, half) - _wma(zl1, s), sq)
    long_c = (n1 > n2).to_numpy()
    tgt = np.where(long_c, 1, -1).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
