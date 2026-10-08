"""Super trend B: the orders come from its 150-bar linear-regression channel: close crossing above
the lower line (regression end value - 2 standard deviations) goes long; crossing below the upper
line goes short (always in).
Port of FMZ strategy #366385 "Super trend B".

Source
    https://www.fmz.com/strategy/366385 (PineScript v5, author Zer3192, FMZ last modified
    2022-05-29 07:09:06). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 85-138), linear length 150, DEV 2
    calcSlope: least squares over the last 150 closes; vwap1 = intercept + slope * 150
    (= linreg(close, 150, 0));  dev = 2 * stdev(close, 150)
    crossover(close, vwap1 - dev) -> entry long; else crossunder(close, vwap1 + dev) -> short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The calcSlope algebra reduces to the regression line at the newest bar. Population stdev.
    * The Bollinger-based SuperTrend lines (buy / sell) only alert; not ported.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header (spot pair in the header only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_366385_linreg_band_cross"
FAMILY = "zscore_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lin_len": [50, 100, 150],
    "dev": [1.5, 2.0, 2.5],
}
DEFAULT_PARAMS = {"lin_len": 150, "dev": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _linreg(y, n, offset=0):
    """ta.linreg(y, n, offset): least-squares line over the last n values (x = 0..n-1),
    evaluated at x = n-1-offset."""
    v = y.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        k = np.arange(n, dtype=float)
        sxy = np.convolve(v, k[::-1], mode="full")[n - 1:len(v)]   # sum_k k * v[t-n+1+k]
        sy = np.convolve(v, np.ones(n), mode="full")[n - 1:len(v)]
        slope = (n * sxy - k.sum() * sy) / (n * (k * k).sum() - k.sum() ** 2)
        intercept = (sy - slope * k.sum()) / n
        out[n - 1:] = intercept + slope * (n - 1 - offset)
    return pd.Series(out, index=y.index)


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["lin_len"])
    mid = _linreg(c, n, 0)
    dev = p["dev"] * c.rolling(n).std(ddof=0)
    lo, up = mid - dev, mid + dev
    buy = ((c > lo) & (c.shift(1) <= lo.shift(1))).to_numpy()
    sell = ((c < up) & (c.shift(1) >= up.shift(1))).to_numpy()
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
