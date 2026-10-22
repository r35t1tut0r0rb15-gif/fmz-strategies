"""Fisher transform (10) turns beyond +- 2.6, 1-hour bars: a Fisher value under -2.6 turning up goes long, over 2.6 turning down goes short; reversing.
Port of FMZ strategy #454341 "Fisher变换动态阈值趋势跟踪策略-Fisher-Transform-Dynamic-Threshold-Trend-Following-Strategy" (Qiuboneminer - Fisher Transform).

FMZ source id: 454341

Source
    https://www.fmz.com/strategy/454341 (PineScript v5, FMZ last modified 2024-06-17 15:01:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-135), Fisher length 10 x 1 on hl2; threshold 2.6
    v = 0.33 x 2 x ((hl2 - min) / (max - min) - 0.5) + 0.67 x nz(v[1]), clamped to +- 0.999;  fish = 0.5 x ln((1 + v) / (1 - v)) + 0.5 x nz(fish[1])
    fish > fish[1] and fish[1] <= fish[2] and fish < -2.6 -> entry Long;  the mirror over 2.6 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The recursions run from 0 (nz) as written; a flat range (max = min) gives na for that bar, and
      nz turns it into 0 on the next. The turn tests use nz on the previous values as written. There is
      no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Fisher transform turns at extremes.
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

NAME = "fmz_454341_fisher_turn_beyond_threshold_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20],
    "threshold": [2.6, 1.5],
}
DEFAULT_PARAMS = {"length": 10, "threshold": 2.6}


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


def _fisher(hl2, n):
    mx, mn = hl2.rolling(n).max().to_numpy(), hl2.rolling(n).min().to_numpy()
    x = hl2.to_numpy(dtype=float)
    m = len(x)
    out = np.full(m, np.nan)
    v_prev = f_prev = np.nan
    for i in range(m):
        rng = mx[i] - mn[i]
        vp = 0.0 if np.isnan(v_prev) else v_prev
        fp = 0.0 if np.isnan(f_prev) else f_prev
        if np.isnan(rng) or rng == 0:
            v = np.nan
        else:
            v = 0.33 * 2 * ((x[i] - mn[i]) / rng - 0.5) + 0.67 * vp
        if np.isnan(v):
            f = np.nan
        else:
            v2 = 0.999 if v > 0.99 else (-0.999 if v < -0.99 else v)
            f = 0.5 * np.log((1 + v2) / (1 - v2)) + 0.5 * fp
        out[i] = f
        v_prev, f_prev = v, f
    return pd.Series(out, index=hl2.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    hl2 = (bars_df["high"] + bars_df["low"]) / 2
    f = _fisher(hl2, int(p["length"]))
    f1, f2 = f.shift(1).fillna(0.0), f.shift(2).fillna(0.0)
    t = float(p["threshold"])
    le = (f > f1) & (f1 <= f2) & (f < -t)
    se = (f < f1) & (f1 >= f2) & (f > t)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
