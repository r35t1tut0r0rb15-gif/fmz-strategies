"""Ehlers MAMA / FAMA (LazyBear's code), 1-hour bars: MAMA crossing above FAMA goes long, crossing below goes short.
Port of FMZ strategy #430662 "基于EMA和MAMA指标的交易策略EMA-and-MAMA-Indicators-Based-Trading-Strategy" (EMAMA strategy).

FMZ source id: 430662

Source
    https://www.fmz.com/strategy/430662 (PineScript v2, FMZ last modified 2023-10-31 14:20:56).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 211-272), source hl2, fast limit 0.5, slow limit 0.05
    Hilbert-transform period p and phase from smoothed hl2 (LazyBear's EMAMA, transcribed line by line)
    alpha = clip(fl / dphase, sl, fl); mama = alpha src + (1 - alpha) mama[1]; fama = 0.5 alpha mama + (1 - 0.5 alpha) fama[1]
    crossover(mama, fama) -> entry long;  crossunder(mama, fama) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Transcribed as written, including Pine's atan in radians (360 / atan(...) and the phase
      difference are therefore not Ehlers' degree values) and nz() on every lagged term. A division by
      zero (q1 / i1 with i1 = 0) is na as in Pine, and an na alpha restarts MAMA / FAMA from 0 on the
      next bar through nz(), as written.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, adaptive moving averages.
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

NAME = "fmz_430662_emama_cross"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_limit": [0.5, 0.3],
    "slow_limit": [0.05, 0.02],
}
DEFAULT_PARAMS = {"fast_limit": 0.5, "slow_limit": 0.05}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _nz(a, i):
    if i < 0:
        return 0.0
    v = a[i]
    return 0.0 if np.isnan(v) else v


def _mama(src, fl, sl):
    m = len(src)
    sp, dt, q1, i1, ji, jq = (np.full(m, np.nan) for _ in range(6))
    i2, q2, re, im, p, p1, p3, ph = (np.full(m, np.nan) for _ in range(8))
    mama, fama = np.full(m, np.nan), np.full(m, np.nan)

    def hilb(x, i):
        return 0.0962 * x[i] + 0.5769 * _nz(x, i - 2) - 0.5769 * _nz(x, i - 4) - 0.0962 * _nz(x, i - 6)

    for i in range(m):
        if i >= 3:
            sp[i] = (4 * src[i] + 3 * src[i - 1] + 2 * src[i - 2] + src[i - 3]) / 10.0
        k = 0.075 * _nz(p, i - 1) + 0.54
        dt[i] = hilb(sp, i) * k
        q1[i] = hilb(dt, i) * k
        i1[i] = _nz(dt, i - 3)
        ji[i] = hilb(i1, i) * k
        jq[i] = hilb(q1, i) * k
        i2_ = i1[i] - jq[i]
        q2_ = q1[i] + ji[i]
        i2[i] = 0.2 * i2_ + 0.8 * _nz(i2, i - 1)
        q2[i] = 0.2 * q2_ + 0.8 * _nz(q2, i - 1)
        re_ = i2[i] * _nz(i2, i - 1) + q2[i] * _nz(q2, i - 1)
        im_ = i2[i] * _nz(q2, i - 1) - q2[i] * _nz(i2, i - 1)
        re[i] = 0.2 * re_ + 0.8 * _nz(re, i - 1)
        im[i] = 0.2 * im_ + 0.8 * _nz(im, i - 1)
        if not np.isnan(im[i]) and not np.isnan(re[i]) and im[i] != 0 and re[i] != 0:
            at = np.arctan(im[i] / re[i])
            p1[i] = 360 / at if at != 0 else np.nan
        else:
            p1[i] = _nz(p, i - 1)
        prev = _nz(p1, i - 1)
        v = p1[i]
        if v > 1.5 * prev:
            v = 1.5 * prev
        elif v < 0.67 * prev:
            v = 0.67 * prev
        if v < 6:
            v = 6.0
        elif v > 50:
            v = 50.0
        p3[i] = v
        p[i] = 0.2 * p3[i] + 0.8 * _nz(p3, i - 1)
        ph[i] = np.arctan(q1[i] / i1[i]) if (not np.isnan(i1[i]) and i1[i] != 0) else np.nan
        dph = _nz(ph, i - 1) - ph[i]
        dph = 1.0 if dph < 1 else dph
        a = fl / dph
        a = sl if a < sl else (fl if a > fl else a)
        mama[i] = a * src[i] + (1 - a) * _nz(mama, i - 1)
        fama[i] = 0.5 * a * mama[i] + (1 - 0.5 * a) * _nz(fama, i - 1)
    return mama, fama


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
    src = ((bars_df["high"] + bars_df["low"]) / 2).to_numpy(dtype=float)
    mama, fama = _mama(src, float(p["fast_limit"]), float(p["slow_limit"]))
    mm, ff = pd.Series(mama, index=bars_df.index), pd.Series(fama, index=bars_df.index)
    xo = ((mm > ff) & (mm.shift(1) <= ff.shift(1))).to_numpy()
    xu = ((mm < ff) & (mm.shift(1) >= ff.shift(1))).to_numpy()
    m = len(src)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if xo[i]:
            pos = 1
        elif xu[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
