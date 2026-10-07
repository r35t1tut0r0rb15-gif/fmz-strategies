"""Broken Fractal: after an up (low) fractal, a close crossing above the last down (high) fractal
goes long; after a down fractal, a bar opening above and closing below the last up-fractal low
goes short (always in).
Port of FMZ strategy #365695 "Broken Fractal".

Source
    https://www.fmz.com/strategy/365695 (PineScript v4, FMZ last modified 2022-05-25 17:21:02).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 66-112), n = 2 (five-bar fractals)
    downFractal = high[2] above high[0], high[1], high[3], high[4]: counter := min(counter, 0) - 1,
                  highAtDownFractal = high[2]
    upFractal   = low[2] below the four neighbours: counter := max(counter, 0) + 1,
                  lowAtUpFractal = low[2]
    sell = counter < 0 and open > lowAtUpFractal and close < lowAtUpFractal
    buy  = counter >= 1 and crossover(close, highAtDownFractal)
    buy -> entry long; else sell -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Fractals are confirmed two bars after the centre (no look-ahead). The stored levels start
      at 0, so nothing fires before the first fractal of each kind.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365695_broken_fractal"
FAMILY = "pivot_reversal"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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
    hs, ls = bars_df["high"], bars_df["low"]
    h2, l2 = hs.shift(2), ls.shift(2)
    down_f = ((hs < h2) & (hs.shift(1) < h2) & (hs.shift(3) < h2) & (hs.shift(4) < h2)).to_numpy()
    up_f = ((ls > l2) & (ls.shift(1) > l2) & (ls.shift(3) > l2) & (ls.shift(4) > l2)).to_numpy()
    o, c = bars_df["open"].to_numpy(dtype=float), bars_df["close"].to_numpy(dtype=float)
    h2v, l2v = h2.to_numpy(), l2.to_numpy()
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    cnt = 0
    hi_lvl = lo_lvl = 0.0
    hi_prev = 0.0
    for i in range(m):
        if down_f[i]:
            cnt = min(cnt, 0) - 1
            hi_lvl = h2v[i]
        if up_f[i]:
            cnt = max(cnt, 0) + 1
            lo_lvl = l2v[i]
        sell = cnt < 0 and o[i] > lo_lvl and c[i] < lo_lvl
        buy = cnt >= 1 and c[i] > hi_lvl and (c[i - 1] if i else np.nan) <= hi_prev
        le[i], se[i] = buy, sell and not buy
        hi_prev = hi_lvl
    return _always_in(le, se, bars_df.index)


def portfolio_kwargs(**params):
    return {}
