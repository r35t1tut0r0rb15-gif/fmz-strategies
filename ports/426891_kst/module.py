"""KST cross (always in): the Know Sure Thing crossing above its 9-bar signal goes long, crossing
below goes short.
Port of FMZ strategy #426891 "KST" (KST-based trend following).

Source
    https://www.fmz.com/strategy/426891 (PineScript v5, FMZ last modified 2023-09-15 12:05:21).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 132-156), ROC 10 / 15 / 20 / 30, SMA 10 / 10 / 10 / 15, signal 9
    kst = sma(roc(close, 10), 10) + 2 sma(roc(15), 10) + 3 sma(roc(20), 10) + 4 sma(roc(30), 15)
    crossover(kst, sma(kst, 9)) -> entry long;  crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.roc = 100 (close - close[n]) / close[n]. The session / new-day variables are unused.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "3h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426891_kst_cross"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-07, user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "scale": [0.5, 1.0, 1.5],
    "siglen": [9, 12],
}
DEFAULT_PARAMS = {"scale": 1.0, "siglen": 9}  # scale multiplies all ROC / SMA lengths


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
    c = bars_df["close"]
    sc = p["scale"]
    L = lambda n: max(1, int(round(n * sc)))
    smaroc = lambda r, s: (100 * (c - c.shift(L(r))) / c.shift(L(r))).rolling(L(s)).mean()
    kst = smaroc(10, 10) + 2 * smaroc(15, 10) + 3 * smaroc(20, 10) + 4 * smaroc(30, 15)
    d = kst - kst.rolling(int(p["siglen"])).mean()
    d1 = d.shift(1)
    return _always_in(((d > 0) & (d1 <= 0)).to_numpy(), ((d < 0) & (d1 >= 0)).to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
