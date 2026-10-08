"""Linear trend (Zer3192): a 200-bar regression channel (4 standard errors) whose lower / upper
lines ratchet like a SuperTrend; the close crossing above the active line goes long, below goes
short (always in).
Port of FMZ strategy #367476 "Linear trend".

Source
    https://www.fmz.com/strategy/367476 (PineScript v4, author Zer3192, FMZ last modified
    2022-06-03 16:09:05). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 40-73), source close, length 200, deviation 4
    lreg = linreg(close, 200, 0); de = regression standard error over the window (as #365345)
    up = lreg - 4 de; down = lreg + 4 de
    up_t := close[1] > up_t[1] ? max(up, up_t[1]) : up;  down_t := close[1] < down_t[1] ? min(down, down_t[1]) : down
    trend := close > down_t[1] ? 1 : close < up_t[1] ? -1 : trend[1] (1 at start)
    line = trend == 1 ? up_t : down_t;  crossover(close, line) -> long; else crossunder -> short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_367476_linreg_channel_trend"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [100, 200],
    "dev": [2.0, 3.0, 4.0],
}
DEFAULT_PARAMS = {"length": 200, "dev": 4.0}


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
    up, down = lr - p["dev"] * de, lr + p["dev"] * de
    up_t, dn_t, line = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    t = 1.0
    for i in range(m):
        u1 = up_t[i - 1] if i else np.nan
        d1 = dn_t[i - 1] if i else np.nan
        c1 = c[i - 1] if i else np.nan
        up_t[i] = max(up[i], u1) if c1 > u1 else up[i]
        dn_t[i] = min(down[i], d1) if c1 < d1 else down[i]
        t = 1.0 if c[i] > d1 else (-1.0 if c[i] < u1 else t)
        line[i] = up_t[i] if t == 1 else dn_t[i]
    lag = lambda a: np.concatenate([[np.nan], a[:-1]])
    buy = (c > line) & (lag(c) <= lag(line))
    sell = (c < line) & (lag(c) >= lag(line))
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
