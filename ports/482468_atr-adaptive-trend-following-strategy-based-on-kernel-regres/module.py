"""A rational-quadratic kernel estimate (27 bars, h 8, r 8) with ATR 32 x 2.7 bands, hourly bars: the close crossing under the lower band goes long, crossing over the upper band goes short; reversing.
Port of FMZ strategy #482468 "基于核回归和ATR动态波段的自适应趋势跟踪策略-Adaptive-Trend-Following-Strategy-Based-on-Kernel-Regression-and-ATR-Dynamic-Bands" (Nadaraya-Watson non repainting Strategy).

FMZ source id: 482468

Source
    https://www.fmz.com/strategy/482468 (PineScript v5, FMZ last modified 2025-02-18 15:33:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-201), kernel h 8, r 8, start bar 25; ATR 32 x 2.7; lag 2 (colours only)
    yhat = sum(close[i] w_i) / sum(w_i), i = 0 .. size + x_0 (size = 1), w_i = (1 + i^2 / (2 r h^2))^-r;  bands = yhat +/- 2.7 atr(32)
    crossunder(close, lower) -> close Short, entry Long;  crossover(close, upper) -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The array holds one value each bar, so the kernel sum runs over i = 0 .. 26 (27 bars) on every bar,
      as written; it is na until 27 bars exist. The second estimate (h - lag) and the colours are display
      only. Each crossing closes the other side and enters, which is a reversal. The source carries the
      Mozilla Public License 2.0 notice. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, kernel-estimate band crossings (counter-trend entries).
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

NAME = "fmz_482468_rq_kernel27_atr32_band_cross_fade_reversal"
FAMILY = "mean_reversion_band"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "coef": [2.7, 2.0],
    "h": [8.0, 16.0],
}
DEFAULT_PARAMS = {"coef": 2.7, "h": 8.0, "r": 8.0, "x_0": 25, "atr_length": 32}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(b, n):
    h, lo, pc = b["high"], b["low"], b["close"].shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def _kernel(x, h, r, terms):
    """Rational-quadratic kernel average of x[t - i], i = 0 .. terms - 1 (na until terms bars exist)."""
    i = np.arange(terms, dtype=float)
    w = (1 + i * i / (h * h * 2 * r)) ** (-r)
    v = x.to_numpy(dtype=float)
    m = len(v)
    out = np.full(m, np.nan)
    if m >= terms:
        out[terms - 1:] = (np.convolve(v, w)[:m] / w.sum())[terms - 1:]
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    yhat = _kernel(c, float(p["h"]), float(p["r"]), 1 + int(p["x_0"]) + 1)
    a = _atr(bars_df, int(p["atr_length"])) * float(p["coef"])
    up, dn = yhat + a, yhat - a
    le = (c < dn) & (c.shift(1) >= dn.shift(1))
    se = (c > up) & (c.shift(1) <= up.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
