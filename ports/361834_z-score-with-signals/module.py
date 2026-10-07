"""Rolling z-score of highs and lows (500 bars): long below -2.5, short above +2.5 (always in).
Port of FMZ strategy #361834 "Z-Score-with-Signals" (Steversteves indicator, orders added).

Source
    https://www.fmz.com/strategy/361834 (PineScript v5, FMZ last modified 2022-05-08 16:33:16).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 59-80)
    c = (high - sma(high,500)) / stdev(high,500);  f = (low - sma(low,500)) / stdev(low,500)
    z = (c + f) / 2
    z < -2.5 -> entry long;  else z > 2.5 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Rolling 500-bar windows ending at the current bar (not whole-series statistics);
      ta.stdev is the population deviation.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361834_hl_zscore_reversion"
FAMILY = "zscore_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [250, 500, 1000],
    "threshold": [2.0, 2.5, 3.0],
}
DEFAULT_PARAMS = {"length": 500, "threshold": 2.5}


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
    h, lo = bars_df["high"], bars_df["low"]
    zh = (h - h.rolling(n).mean()) / h.rolling(n).std(ddof=0)
    zl = (lo - lo.rolling(n).mean()) / lo.rolling(n).std(ddof=0)
    z = ((zh + zl) / 2).to_numpy()
    return _always_in(z < -p["threshold"], z > p["threshold"], bars_df.index)


def portfolio_kwargs(**params):
    return {}
