"""Darvas box: a box top / bottom fixed three bars after a new 5-bar high (when the high has not
been exceeded since); the close crossing above the box top goes long, crossing below the box
bottom goes short (always in).
Port of FMZ strategy #366948 "Darvas Box Buy Sell".

Source
    https://www.fmz.com/strategy/366948 (PineScript v4, FMZ last modified 2022-05-31 19:31:56).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 44-72), length 5
    k1 = highest(high, 5); k2 = highest(high, 4); k3 = highest(high, 3); LL = lowest(low, 5)
    NH = valuewhen(high > k1[1], high, 0)
    when barssince(high > k1[1]) == 3 and k3 < k2: TopBox = NH, BottomBox = LL
    crossover(close, TopBox) -> entry long; else crossunder(close, BottomBox) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The boxes are na until the first one forms. strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "45min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_366948_darvas_box_break"
FAMILY = "donchian_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "boxp": [4, 5, 8, 13],
}
DEFAULT_PARAMS = {"boxp": 5}


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
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["boxp"])
    hs, ls = bars_df["high"], bars_df["low"]
    k1 = hs.rolling(n).max()
    k2 = hs.rolling(n - 1).max().to_numpy()
    k3 = hs.rolling(max(n - 2, 1)).max().to_numpy()
    ll = ls.rolling(n).min().to_numpy()
    new_hi = (hs > k1.shift(1)).to_numpy()
    h, c = hs.to_numpy(dtype=float), bars_df["close"].to_numpy(dtype=float)
    m = len(h)
    top, bot = np.full(m, np.nan), np.full(m, np.nan)
    nh = np.nan
    last = -1
    for i in range(m):
        if new_hi[i]:
            nh, last = h[i], i
        t_prev = top[i - 1] if i else np.nan
        b_prev = bot[i - 1] if i else np.nan
        if last >= 0 and i - last == n - 2 and k3[i] < k2[i]:
            top[i], bot[i] = nh, ll[i]
        else:
            top[i], bot[i] = t_prev, b_prev
    lag = lambda a: np.concatenate([[np.nan], a[:-1]])
    buy = (c > top) & (lag(c) <= lag(top))
    sell = (c < bot) & (lag(c) >= lag(bot))
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
