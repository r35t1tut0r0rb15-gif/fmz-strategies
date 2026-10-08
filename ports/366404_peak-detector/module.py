"""Peak detector (Zer3192): a low dipping 5 % below the lower line of a 100-bar linear-regression
channel (2 standard errors) goes long; a high poking 5 % above the upper line goes short.
Port of FMZ strategy #366404 "Peak detector".

Source
    https://www.fmz.com/strategy/366404 (PineScript v4, author Zer3192, FMZ last modified
    2022-05-29 09:32:08). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 43-73), source close, length 100, deviation 2, 5 % / 5 %
    lreg = linreg(close, 100, 0); slope = lreg - linreg(close, 100, 1)
    de = sqrt(mean over i = 0..99 of (close[i] - (lreg - slope * i))^2)
    lower = lreg - 2 de ("up");  upper = lreg + 2 de ("down")
    crossunder(low, 0.95 * lower) -> entry long; else crossover(high, 1.05 * upper) -> short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The author's line names are swapped ("up" is the lower line); the orders are as coded.
    * Same channel as #365345; the 5 % margins are relative (scale-free).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header (spot pair in the header only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_366404_linreg_peak_reversion"
FAMILY = "zscore_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 100],
    "dev": [1.5, 2.0],
    "pct": [2.0, 5.0],
}
DEFAULT_PARAMS = {"length": 100, "dev": 2.0, "pct": 5.0}


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
    de = np.full(m, np.nan)
    k = np.arange(n)
    for t in range(n - 1, m):
        de[t] = np.sqrt(np.mean((c[t - k] - (lr[t] - slope[t] * k)) ** 2))
    lower = (1 - p["pct"] / 100) * (lr - p["dev"] * de)
    upper = (1 + p["pct"] / 100) * (lr + p["dev"] * de)
    lo, hi = bars_df["low"].to_numpy(dtype=float), bars_df["high"].to_numpy(dtype=float)
    lag = lambda a: np.concatenate([[np.nan], a[:-1]])
    buy = (lo < lower) & (lag(lo) >= lag(lower))
    sell = (hi > upper) & (lag(hi) <= lag(upper))
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
