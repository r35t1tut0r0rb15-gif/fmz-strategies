"""SMA 4 / 34 cross (always in): SMA 34 crossing above SMA 4 goes short, crossing below goes long.
Port of FMZ strategy #426335 "SMA Crossover Trading Strategy".

Source
    https://www.fmz.com/strategy/426335 (PineScript v3, FMZ last modified 2023-09-11 11:42:52).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 85-93)
    crossover(sma(close, 34), sma(close, 4))  -> entry short   (checked first)
    crossunder(sma(close, 34), sma(close, 4)) -> entry long

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "10min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426335_sma_4_34_cross"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [4, 8],
    "slow": [34, 55],
}
DEFAULT_PARAMS = {"fast": 4, "slow": 34}


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
    d = c.rolling(int(p["slow"])).mean() - c.rolling(int(p["fast"])).mean()
    d1 = d.shift(1)
    short = ((d > 0) & (d1 <= 0)).to_numpy()
    long_ = ((d < 0) & (d1 >= 0)).to_numpy()
    return _always_in(long_, short, bars_df.index, short_first=True)


def portfolio_kwargs(**params):
    return {}
