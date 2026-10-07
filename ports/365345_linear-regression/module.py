"""Linear regression channel (Lucem Anb): close crossing below the lower channel (regression line
- 2 standard errors over 100 bars) goes long; crossing above the upper channel goes short.
Port of FMZ strategy #365345 "Linear Regression ++ [Lucem Anb]".

Source
    https://www.fmz.com/strategy/365345 (PineScript v4, FMZ last modified 2022-05-24 14:17:42).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 89-140), source close, length 100, deviation 2,
smoothing 1, resolution "" (chart)
    lr = linreg(close, 100, 0); slope = lr - linreg(close, 100, 1)
    deviation = sqrt(mean over i = 0..99 of (close[i] - (lr - slope * i))^2)
    buy = crossunder(close, lr - 2 * deviation) -> entry long
    else sell = crossover(close, lr + 2 * deviation) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Resolution "" is the chart; smoothing 1 is the series itself. The channel is in price
      units but built from the series' own dispersion (scale-free).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "45min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365345_linreg_channel_reversion"
FAMILY = "zscore_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 100, 200],
    "dev": [1.5, 2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 100, "dev": 2.0}


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
    cs = bars_df["close"]
    n = int(p["length"])
    lr = _linreg(cs, n, 0).to_numpy()
    slope = lr - _linreg(cs, n, 1).to_numpy()
    c = cs.to_numpy(dtype=float)
    m = len(c)
    dev = np.full(m, np.nan)
    k = np.arange(n, dtype=float)  # i = 0..n-1 bars back
    for t in range(n - 1, m):
        w = c[t - k.astype(int)]
        dev[t] = np.sqrt(np.mean((w - (lr[t] - slope[t] * k)) ** 2))
    lower, upper = lr - p["dev"] * dev, lr + p["dev"] * dev
    c1 = np.concatenate([[np.nan], c[:-1]])
    lo1 = np.concatenate([[np.nan], lower[:-1]])
    up1 = np.concatenate([[np.nan], upper[:-1]])
    buy = (c < lower) & (c1 >= lo1)
    sell = (c > upper) & (c1 <= up1)
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
