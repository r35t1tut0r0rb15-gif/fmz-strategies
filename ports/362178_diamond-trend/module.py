"""Parabolic SAR with a regression-residual band, ratcheted like a SuperTrend; close crossing the
active band line flips the position ("Diamond Trend" / PSAR x).
Port of FMZ strategy #362178 "Diamond-Trend".

Source
    https://www.fmz.com/strategy/362178 (PineScript v4, FMZ last modified 2022-05-10 14:47:48).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 46-79), SAR 0.02/0.02/0.2, len 100, dev 1.9
    psar = sar(0.02, 0.02, 0.2); lreg = linreg(psar,100,0); s = lreg - linreg(psar,100,1)
    de = sqrt(mean over the last 100 bars of (psar[i] - (lreg - s*i))^2)
    up = psar - 1.9*de; down = psar + 1.9*de; up_t/down_t ratchet; trend flips on closes
    r_line = trend == 1 ? up_t : down_t
    crossover(close, r_line) -> entry long;  else crossunder(close, r_line) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * sar is TradingView's documented pine_sar algorithm. The residual sum is computed in closed
      form over the same 100-bar window (no future values).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "15min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362178_psar_regression_band_flip"
FAMILY = "parabolic_sar"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 100, 200],
    "dev": [1.5, 1.9, 2.5],
}
DEFAULT_PARAMS = {"start": 0.02, "increment": 0.02, "maximum": 0.2, "length": 100, "dev": 1.9}


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


def _sar_pine(bars, start, inc, maximum):
    """ta.sar as TradingView documents it (pine_sar): starts on bar 1, direction from close vs
    the previous close; value capped by the previous two bars' lows (highs)."""
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    out = np.full(m, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, m):
        first = False
        if i == 1:
            if c[1] > c[0]:
                below, max_min, result = True, h[1], lo[0]
            else:
                below, max_min, result = False, lo[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if below:
            if result > lo[i]:
                first, below = True, False
                result, max_min, acc = max(h[i], max_min), lo[i], start
        else:
            if result < h[i]:
                first, below = True, True
                result, max_min, acc = min(lo[i], max_min), h[i], start
        if not first:
            if below and h[i] > max_min:
                max_min, acc = h[i], min(acc + inc, maximum)
            elif (not below) and lo[i] < max_min:
                max_min, acc = lo[i], min(acc + inc, maximum)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return pd.Series(out, index=bars.index)


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
    n = int(p["length"])
    ps = _sar_pine(bars_df, p["start"], p["increment"], p["maximum"])
    lreg = _linreg(ps, n, 0)
    s = (lreg - _linreg(ps, n, 1)).to_numpy()
    a = lreg.to_numpy()
    y = ps.to_numpy(dtype=float)
    k = np.arange(n, dtype=float)
    sy = np.full(len(y), np.nan)
    sy2 = np.full(len(y), np.nan)
    siy = np.full(len(y), np.nan)
    if len(y) >= n:
        sy[n - 1:] = np.convolve(y, np.ones(n), mode="full")[n - 1:len(y)]
        sy2[n - 1:] = np.convolve(y * y, np.ones(n), mode="full")[n - 1:len(y)]
        siy[n - 1:] = np.convolve(y, k, mode="full")[n - 1:len(y)]       # sum_i i * y[t-i]
    si, si2 = k.sum(), (k * k).sum()
    ds = sy2 - 2 * a * sy + 2 * s * siy + n * a * a - 2 * a * s * si + s * s * si2
    de = np.sqrt(np.clip(ds, 0, None) / n)
    up, down = y - de * p["dev"], y + de * p["dev"]
    c = bars_df["close"].to_numpy(dtype=float)
    m = len(c)
    up_t, dn_t, r = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    trend = 1
    for i in range(m):
        pu = up_t[i - 1] if i else np.nan
        pd_ = dn_t[i - 1] if i else np.nan
        up_t[i] = max(up[i], pu) if (i and c[i - 1] > pu) else up[i]
        dn_t[i] = min(down[i], pd_) if (i and c[i - 1] < pd_) else down[i]
        trend = 1 if c[i] > pd_ else (-1 if c[i] < pu else trend)
        r[i] = up_t[i] if trend == 1 else dn_t[i]
    r1, c1 = np.roll(r, 1), np.roll(c, 1)
    r1[0] = np.nan
    buy = (c > r) & (c1 <= r1)
    sell = (c < r) & (c1 >= r1)
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
