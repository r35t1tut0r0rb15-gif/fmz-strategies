"""Voss predictive filter with Ehlers' instantaneous trendline: while the trendline's lag line is
below the trendline, the Voss predictor crossing above its band-pass filter goes long and the
filter crossing above the predictor goes short (always in the market after the first signal).
Port of FMZ strategy #427275 "Quantitative Trading Strategy Based on Voss Filter and Trend Indicator".

FMZ source id: 427275

Source
    https://www.fmz.com/strategy/427275 (PineScript v4, FMZ last modified 2023-09-19 16:59:10).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 205-297), period 20, predict 4, bandwidth 0.25, IT alpha 0.07 on hl2
    filt = 0.5 s3 (close - close[2]) + f1 s2 filt[1] - s1 filt[2]   (0 for bar_index <= order = 12)
    voss = x2 filt - sum_{i=0..order-1} (i + 1) / order x voss[order - i]
    it = Ehlers instantaneous trendline of hl2 (alpha 0.07); lag = 2 it - it[2]
    lag < it and crossover(voss, filt) -> entry long; it > lag and crossover(filt, voss) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written, both entries need the same trend test (lag < it is it > lag).
    * bar_index counts bars from the first bar of the data (the filter is 0 for the first 13 bars).
    * nz() seeds of the trendline as written: (src + 2 src[1] + src[2]) / 4 where it[1] / it[2]
      do not exist yet; nz(it[2]) = 0 in the lag for the first two bars.
    * isPeriod is the constant true: the backtest-window close-out never fires (dropped).
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; recursive filters on past bars only.
    2 generic: PASS, the filters are linear in price (scale-free crosses).
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

NAME = "fmz_427275_voss_instantaneous_trend"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [20, 40],
    "predict": [4, 2],
    "alpha": [0.07, 0.15],
}
DEFAULT_PARAMS = {"period": 20, "predict": 4, "bandwidth": 0.25, "alpha": 0.07}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _voss(src, period, predict, bandwidth):
    order = 3 * predict
    f1 = np.cos(2 * np.pi / period)
    g1 = np.cos(bandwidth * 2 * np.pi / period)
    s1 = 1 / g1 - np.sqrt(1 / (g1 * g1) - 1)
    s2, s3 = 1 + s1, 1 - s1
    x2 = (3 + order) / 2
    m = len(src)
    filt, voss = np.zeros(m), np.zeros(m)
    for t in range(m):
        sumc = 0.0
        for i in range(order):
            k = t - (order - i)
            sumc += (i + 1) / order * (voss[k] if k >= 0 else np.nan)
        if t <= order:
            filt[t], voss[t] = 0.0, 0.0
        else:
            x1 = src[t] - src[t - 2]
            filt[t] = 0.5 * s3 * x1 + f1 * s2 * filt[t - 1] - s1 * filt[t - 2]
            voss[t] = x2 * filt[t] - sumc
    return voss, filt


def _itrend(src, a):
    m = len(src)
    it = np.full(m, np.nan)
    for t in range(m):
        s0 = src[t]
        s1_ = src[t - 1] if t >= 1 else np.nan
        s2_ = src[t - 2] if t >= 2 else np.nan
        seed = (s0 + 2 * s1_ + s2_) / 4.0
        i1 = it[t - 1] if t >= 1 and not np.isnan(it[t - 1]) else seed
        i2 = it[t - 2] if t >= 2 and not np.isnan(it[t - 2]) else seed
        it[t] = ((a - a * a / 4.0) * s0 + 0.5 * a * a * s1_ - (a - 0.75 * a * a) * s2_
                 + 2 * (1 - a) * i1 - (1 - a) * (1 - a) * i2)
    it2 = np.concatenate(([np.nan, np.nan], it[:-2]))
    lag = 2.0 * it - np.where(np.isnan(it2), 0.0, it2)
    return it, lag


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
    c = bars_df["close"].to_numpy(dtype=float)
    hl2 = ((bars_df["high"] + bars_df["low"]) / 2).to_numpy(dtype=float)
    v, f = _voss(c, float(p["period"]), int(p["predict"]), float(p["bandwidth"]))
    it, lag = _itrend(hl2, float(p["alpha"]))
    v1 = np.concatenate(([np.nan], v[:-1]))
    f1 = np.concatenate(([np.nan], f[:-1]))
    trend = lag < it
    long_c = trend & (v > f) & (v1 <= f1)
    short_c = trend & (f > v) & (f1 <= v1)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if short_c[i] and pos != -1:       # the short entry comes first in the script
            pos = -1
        elif long_c[i] and pos != 1:
            pos = 1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
