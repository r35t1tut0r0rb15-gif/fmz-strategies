"""Stacked rising SMAs with zero-lag EMA exits, 2-hour bars: SMA 10 > 20 > 50 > 100 with the 10 / 20 / 100 / 200 all rising over 4 bars goes long, the falling mirror (10 < 20 < 50) short; the zero-lag
EMA 9 / 21 or the SMA 10 / 20 crossing back closes; reversing.
Port of FMZ strategy #440976 "基于多周期SMA指标的趋势跟踪策略Trend-Following-Strategy-Based-on-Multi-Period-SMA" (FX MA Racer (5x SMA, 2x zlEMA)).

FMZ source id: 440976

Source
    https://www.fmz.com/strategy/440976 (PineScript v2, FMZ last modified 2024-02-04 14:50:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 132-242), SMA 10 / 20 / 50 / 100 / 200; direction span 4; zero-lag EMA 9 / 21; time limiter from 2018; trailing stop off
    longCond = sma10 > sma20 > sma50 > sma100 and rising(10, 20, 100, 200 over 4);  shortCond = sma10 < sma20 < sma50 and falling(...);  entry long / short
    longExit = crossunder(zlemaFast, zlemaSlow) or crossunder(sma10, sma20) -> close long;  shortExit mirrored -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * rising(x, 4) is x above each of its previous 4 values (falling mirrored). The entries are levels;
      the closes are written after them and act only on the held position, so a reversing entry stands
      (as #438020). The time limiter is never applied (the block runs unconditionally) and the trailing
      stop is off. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "2h" from the
      backtest header (bars on UTC multiples of 2 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA stack slopes and zero-lag EMA crossings.
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

NAME = "fmz_440976_sma_racer_zero_lag_exits"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "dir_span": [4, 8],
    "zl_slow": [21, 34],
}
DEFAULT_PARAMS = {"dir_span": 4, "zl_slow": 21, "zl_fast": 9}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    s = {n: c.rolling(n).mean() for n in (10, 20, 50, 100, 200)}
    k = int(p["dir_span"])

    def rising(x):
        return x > x.shift(1).rolling(k).max()

    def falling(x):
        return x < x.shift(1).rolling(k).min()

    up = rising(s[10]) & rising(s[20]) & rising(s[100]) & rising(s[200])
    dn = falling(s[10]) & falling(s[20]) & falling(s[100]) & falling(s[200])
    L = ((s[10] > s[20]) & (s[20] > s[50]) & (s[50] > s[100]) & up).to_numpy()
    S = ((s[10] < s[20]) & (s[20] < s[50]) & dn).to_numpy()

    def zl(n):
        e1 = c.ewm(span=n, adjust=False).mean()
        return 2 * e1 - e1.ewm(span=n, adjust=False).mean()

    zf, zs = zl(int(p["zl_fast"])), zl(int(p["zl_slow"]))

    def xo(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    XL = (xo(zs, zf) | xo(s[20], s[10])).to_numpy()
    XS = (xo(zf, zs) | xo(s[10], s[20])).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if L[i]:
            new = 1
        if S[i]:
            new = -1
        if XL[i] and pos == 1 and new == 1:
            new = 0
        if XS[i] and pos == -1 and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
