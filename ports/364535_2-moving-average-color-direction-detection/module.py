"""Two moving averages: SMA 20 crossing below SMA 8 (the fast one moving above) goes long; SMA 8
crossing below SMA 20 goes short (always in).
Port of FMZ strategy #364535 "2 Moving Average Color Direction Detection".

Source
    https://www.fmz.com/strategy/364535 (PineScript v3, FMZ last modified 2022-05-20 16:44:13).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 55-154), 1-MA SMA 20, 2-MA SMA 8 (both on close)
    crossunder(ma_20, ma_8) -> entry long; else crossunder(ma_8, ma_20) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The rising/falling colour directions only draw and feed alerts.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * No bar size in the source: FREQ = "bar_size_pending" (rule 1, 2026-10-07).

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_364535_sma_8_20_cross"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "bar_size_pending"  # no bar size in the source (rule 1, 2026-10-07)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slow": [20, 30, 50],
    "fast": [5, 8, 13],
}
DEFAULT_PARAMS = {"slow": 20, "fast": 8}


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
    a, b = c.rolling(int(p["slow"])).mean(), c.rolling(int(p["fast"])).mean()
    long_ = ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()
    short = ((b < a) & (b.shift(1) >= a.shift(1))).to_numpy()
    return _always_in(long_, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
