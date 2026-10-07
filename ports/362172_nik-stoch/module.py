"""Fast stochastic (5,3,3) %K/%D crosses traded as written: %K crossing ABOVE %D goes SHORT,
crossing below goes LONG (always in).
Port of FMZ strategy #362172 "Nik-Stoch".

Source
    https://www.fmz.com/strategy/362172 (PineScript v5, FMZ last modified 2022-05-10 14:08:03).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 45-75)
    k1 = sma(stoch(close, high, low, 5), 3); d1 = sma(k1, 3)
    k1[1] < d1[1] and k1 > d1 -> entry short;  else k1[1] > d1[1] and k1 < d1 -> entry long
    (the 14-period pair is plotted only)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362172_fast_stoch_cross_faded"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "k_len": [5, 9, 14],
    "smooth": [3, 5],
}
DEFAULT_PARAMS = {"k_len": 5, "smooth": 3, "d_len": 3}


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
    n = int(p["k_len"])
    hh, ll = bars_df["high"].rolling(n).max(), bars_df["low"].rolling(n).min()
    st = (100 * (bars_df["close"] - ll) / (hh - ll)).replace([np.inf, -np.inf], np.nan)
    k = st.rolling(int(p["smooth"])).mean()
    d = k.rolling(int(p["d_len"])).mean()
    up = ((k.shift(1) < d.shift(1)) & (k > d)).to_numpy()
    dn = ((k.shift(1) > d.shift(1)) & (k < d)).to_numpy()
    return _always_in(dn, up, bars_df.index)


def portfolio_kwargs(**params):
    return {}
