"""Order Block Finder: a red candle followed by seven green candles (a bullish order block, seen
on the seventh) goes long; a green candle followed by seven red ones goes short (always in).
Port of FMZ strategy #365075 "Order Block Finder".

Source
    https://www.fmz.com/strategy/365075 (PineScript v4, FMZ last modified 2022-05-23 13:54:57).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 57-124), periods 7, threshold 0 %
    bullishOB = close[8] < open[8]; upcandles = count(close[i] > open[i], i = 1..7)
    relmove = |close[8] - close[1]| / close[8] * 100 >= threshold
    OB_bull = bullishOB and upcandles == 7 and relmove -> entry long
    else OB_bear (green [8], seven red) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * security(res = "") is the chart series itself. The threshold is a percent move
      (scale-free); with 0 it only needs the values to exist.
    * The current bar's own candle is not part of the pattern, as coded.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365075_order_block_sequence"
FAMILY = "candle_pattern"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "periods": [5, 7, 9],
    "threshold": [0.0, 1.0],
}
DEFAULT_PARAMS = {"periods": 7, "threshold": 0.0}


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
    o, c = bars_df["open"], bars_df["close"]
    n = int(p["periods"])
    k = n + 1
    green = (c > o).astype(float)
    red = (c < o).astype(float)
    ups = green.shift(1).rolling(n).sum()
    downs = red.shift(1).rolling(n).sum()
    move = ((c.shift(k) - c.shift(1)).abs() / c.shift(k)) * 100
    rel = move >= p["threshold"]
    bull = ((c.shift(k) < o.shift(k)) & (ups == n) & rel).to_numpy()
    bear = ((c.shift(k) > o.shift(k)) & (downs == n) & rel).to_numpy()
    return _always_in(bull, bear, bars_df.index)


def portfolio_kwargs(**params):
    return {}
