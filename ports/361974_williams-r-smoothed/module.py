"""Smoothed Williams %R turns: long when the WMA-smoothed %R turns up below -30, short when it
turns down above -70 (always in).
Port of FMZ strategy #361974 "Williams-R-Smoothed" ("The Smooth Willy", orders added).

Source
    https://www.fmz.com/strategy/361974 (PineScript v5, FMZ last modified 2022-05-09 12:08:11).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 60-102), length 34, fast 5
    output = 100*(close - highest(high,34)) / (highest - lowest(low,34));  fast = wma(output, 5)
    bullreverse = fast[2] > fast[1] and fast > fast[1] and fast < -30 -> entry long
    bearreverse = fast[2] < fast[1] and fast < fast[1] and fast > -70 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The EMA crossover signals are plotted only. `plotRev` is true by default.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361974_smoothed_williams_r_turns"
FAMILY = "williams_r_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 34, 55],
    "fast": [3, 5, 8],
}
DEFAULT_PARAMS = {"length": 34, "fast": 5}


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
    hh, ll = bars_df["high"].rolling(n).max(), bars_df["low"].rolling(n).min()
    out = (100 * (bars_df["close"] - hh) / (hh - ll)).replace([np.inf, -np.inf], np.nan)
    f = _wma(out, int(p["fast"]))
    bull = ((f.shift(2) > f.shift(1)) & (f > f.shift(1)) & (f < -30)).to_numpy()
    bear = ((f.shift(2) < f.shift(1)) & (f < f.shift(1)) & (f > -70)).to_numpy()
    return _always_in(bull, bear, bars_df.index)


def portfolio_kwargs(**params):
    return {}
