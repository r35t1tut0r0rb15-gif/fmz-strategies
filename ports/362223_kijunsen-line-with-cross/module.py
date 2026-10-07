"""HL2 crossing the Kijun-sen (midpoint of the 26-bar range), stop-and-reverse.
Port of FMZ strategy #362223 "KijunSen-Line-With-Cross" (dilan1999).

Source
    https://www.fmz.com/strategy/362223 (PineScript v5, FMZ last modified 2022-05-10 18:56:36).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 39-59), n 26
    value = (highest(high,26) + lowest(low,26)) / 2
    crossover(hl2, value) -> entry long;  else crossunder(hl2, value) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * No backtest header: FREQ = "bar_size_pending" (rule 1).

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_362223_hl2_kijun_cross"
FAMILY = "ichimoku"  # proposed 2026-10-07, user to confirm
FREQ = "bar_size_pending"  # source declares no bar size; set by the project before running
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [9, 26, 52],
}
DEFAULT_PARAMS = {"n": 26}


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
    n = int(p["n"])
    h, lo = bars_df["high"], bars_df["low"]
    value = (h.rolling(n).max() + lo.rolling(n).min()) / 2
    hl2 = (h + lo) / 2
    up = ((hl2 > value) & (hl2.shift(1) <= value.shift(1))).to_numpy()
    dn = ((hl2 < value) & (hl2.shift(1) >= value.shift(1))).to_numpy()
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
