"""Closes crossing out of a 2.7 ATR envelope around a rational-quadratic kernel average: below the lower band goes
long, above the upper band goes short, always in, hourly bars.
Port of FMZ strategy #482468 "基于核回归和ATR动态波段的自适应趋势跟踪策略-Adaptive-Trend-Following-Strategy-Based-on-Kernel-Regression-and-ATR-Dynamic-Bands" (Nadaraya-Watson non repainting Strategy).

FMZ source id: 482468

Source
    https://www.fmz.com/strategy/482468 (PineScript v5, FMZ last modified 2025-02-18 15:33:21).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 99-201), h 8, r 8, x_0 25, ATR 32 x 2.7
    yhat = sum(close[i] w_i) / sum(w_i), i = 0..26, w_i = (1 + i^2 / (2 r h^2))^-r (past bars only; the loop runs to
    size + x_0 with size = 1)
    crossunder(close, yhat - 2.7 ATR) -> close short, entry long; crossover(close, yhat + 2.7 ATR) -> close long,
    entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The kernel sums lags 0-26 of the close (the array holds one value, so the loop bound is 1 + 25); na until 27
      bars exist. The second (lagged-h) estimate and the colours feed no order.
    * The closes repeat the reversal of the entries (REVERSAL INTENDED); always in. Signal module, no stops.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a kernel average and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
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

NAME = "fmz_482468_rq_kernel_atr_envelope_fade_always_in"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "coef": [2.7, 2.0],
    "h": [8.0, 16.0],
}
DEFAULT_PARAMS = {"h": 8.0, "r": 8.0, "x_0": 25, "atr_len": 32, "coef": 2.7}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _kernel(c, h, r, x_0):
    k = 1 + x_0 + 1                                       # i = 0 .. size + x_0, size = 1
    i = np.arange(k, dtype=float)
    w = (1 + i ** 2 / (h ** 2 * 2 * r)) ** (-r)
    v = c.to_numpy(dtype=float)
    out = np.convolve(v, w)[:len(v)] / w.sum()            # out[t] = sum_i v[t - i] w[i] / sum w
    out[:k - 1] = np.nan
    return pd.Series(out, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    yhat = _kernel(c, float(p["h"]), float(p["r"]), int(p["x_0"]))
    band = p["coef"] * _atr(bars_df, int(p["atr_len"]))
    upper, lower = yhat + band, yhat - band
    long_e = ((c < lower) & (c.shift(1) >= lower.shift(1))).astype(bool)
    short_e = ((c > upper) & (c.shift(1) <= upper.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
