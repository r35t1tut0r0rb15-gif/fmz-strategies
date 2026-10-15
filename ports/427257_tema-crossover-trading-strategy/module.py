"""TEMA 34 / TEMA 13 cross: when the two cross and the slow TEMA ends below the fast one, go long;
when they cross and the slow one ends above, go short (always in the market after the first cross).
Port of FMZ strategy #427257 "TEMA Crossover Trading Strategy".

FMZ source id: 427257

Source
    https://www.fmz.com/strategy/427257 (PineScript v2, FMZ last modified 2023-09-19 15:41:47).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 156-198), lengths 34 and 13
    nRes = TEMA(close, 34); nRes2 = TEMA(close, 13)
    cross(nRes, nRes2) and nRes < nRes2 -> entry long; cross and nRes > nRes2 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * TEMA = 3 e1 - 3 e2 + e3 of chained EMAs (ewm adjust False). cross() = either direction.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "30min" from the backtest header.

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

NAME = "fmz_427257_tema_cross"
FAMILY = "ma_trend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slow": [34, 55, 21],
    "fast": [13, 8],
}
DEFAULT_PARAMS = {"slow": 34, "fast": 13}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _tema(x, n):
    e1 = x.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    e3 = e2.ewm(span=n, adjust=False).mean()
    return 3 * e1 - 3 * e2 + e3


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
    c = bars_df["close"]
    a, b = _tema(c, int(p["slow"])), _tema(c, int(p["fast"]))
    crossed = ((a > b) & (a.shift(1) <= b.shift(1))) | ((a < b) & (a.shift(1) >= b.shift(1)))
    long_c = (crossed & (a < b)).to_numpy()
    short_c = (crossed & (a > b)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i]:
            pos = 1
        elif short_c[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
