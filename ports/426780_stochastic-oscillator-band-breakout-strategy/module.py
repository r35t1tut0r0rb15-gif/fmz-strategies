"""Stochastic bands (HPotter, always in): %K(7) above 20 goes long; otherwise %K below 80 goes short.
As written the long test comes first, so the short side only fires when %K is at or under 20.
Port of FMZ strategy #426780 "Stochastic Oscillator Band Breakout Strategy".

Source
    https://www.fmz.com/strategy/426780 (PineScript v2/v3 syntax, FMZ last modified 2023-09-14 15:31:25).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 134-151), Length 7, UpBand 20, DownBand 80
    vFast = stoch(close, high, low, 7)
    pos = vFast > 20 ? 1 : vFast < 80 ? -1 : previous;  1 -> entry long, -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Kept as written: with UpBand 20 < DownBand 80 the long branch covers %K > 20 (decision
      owed: the bands look swapped). %K over a flat range is na, keeping the previous state.
    * The %D line only plots. "Trade reverse" off. REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426780_stochastic_bands"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [7, 14],
    "up_band": [20, 50],
    "down_band": [80, 50],
}
DEFAULT_PARAMS = {"length": 7, "up_band": 20, "down_band": 80}


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
    n = int(p["length"])
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    lo, hi = l.rolling(n).min(), h.rolling(n).max()
    k = 100 * (c - lo) / (hi - lo)
    return _always_in((k > p["up_band"]).to_numpy(), (k < p["down_band"]).to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
