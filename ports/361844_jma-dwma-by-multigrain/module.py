"""Jurik MA (simple form) vs double-WMA cross entries; each side is closed early at a JMA local
peak (long) or trough (short) that forms on the right side of the DWMA.
Port of FMZ strategy #361844 "jma-dwma-by-multigrain".

Source
    https://www.fmz.com/strategy/361844 (PineScript v5, FMZ last modified 2022-05-09 00:17:15).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 58-101), JMA close 7 phase 50 power 1, DWMA close 10
    jma (e0/e1/e2 recursion); dwma = wma(wma(close,10),10)
    long = crossover(jma, dwma);  long_tp = pivothigh(jma,1,1) and jma > dwma
    short = crossunder(jma, dwma); short_tp = pivotlow(jma,1,1) and jma < dwma
    entry Buy when long; close Buy when long_tp; entry Sell when short; close Sell when short_tp

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: a cross while in the opposite side reverses (REVERSAL INTENDED,
      portfolio_kwargs {}). strategy.close -> exit signals; a close on the bar of a new entry
      does nothing (no filled position yet).
    * pivothigh(jma,1,1): jma[1] strictly above jma[2] and jma[0], confirmed on the current bar.
    * The "JMA Power" input default is `true` in FMZ's argument table, i.e. 1.
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361844_jma_dwma_cross_pivot_exit"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "jma_len": [5, 7, 14],
    "dwma_len": [5, 10, 20],
}
DEFAULT_PARAMS = {"jma_len": 7, "jma_phase": 50, "jma_power": 1.0, "dwma_len": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _jma_simple(src, length, phase, power):
    s = src.to_numpy(dtype=float)
    pr = 0.5 if phase < -100 else (2.5 if phase > 100 else phase / 100 + 1.5)
    beta = 0.45 * (length - 1) / (0.45 * (length - 1) + 2)
    alpha = beta ** power
    e0 = e1 = e2 = jma = 0.0
    out = np.full(len(s), np.nan)
    for t in range(len(s)):
        e0 = (1 - alpha) * s[t] + alpha * e0
        e1 = (s[t] - e0) * (1 - beta) + beta * e1
        e2 = (e0 + pr * e1 - jma) * (1 - alpha) ** 2 + alpha ** 2 * e2
        jma = out[t] = e2 + jma
    return pd.Series(out, index=src.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    j = _jma_simple(c, int(p["jma_len"]), p["jma_phase"], p["jma_power"])
    d = _wma(_wma(c, int(p["dwma_len"])), int(p["dwma_len"]))
    up = ((j > d) & (j.shift(1) <= d.shift(1))).to_numpy()
    dn = ((j < d) & (j.shift(1) >= d.shift(1))).to_numpy()
    peak = ((j.shift(1) > j.shift(2)) & (j.shift(1) > j) & (j > d)).to_numpy()
    trough = ((j.shift(1) < j.shift(2)) & (j.shift(1) < j) & (j < d)).to_numpy()

    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        prev = pos
        if up[i] and pos != 1:
            le[i], pos = True, 1
        if peak[i] and prev == 1 and pos == 1:
            lx[i], pos = True, 0
        if dn[i] and pos != -1:
            se[i], pos = True, -1
        if trough[i] and prev == -1 and pos == -1:
            sx[i], pos = True, 0

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
