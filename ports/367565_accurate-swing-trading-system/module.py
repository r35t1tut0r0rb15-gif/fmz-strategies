"""Accurate swing trading system (Zer3192): a 3-bar swing stop line (lowest low after a breakout up,
highest high after a breakout down); the close crossing above it goes long, below goes short.
Port of FMZ strategy #367565 "Accurate Swing Trading System".

Source
    https://www.fmz.com/strategy/367565 (PineScript v4, author Zer3192, FMZ last modified
    2022-06-04 07:05:48). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 39-65), swing 3
    res = highest(high, 3); sup = lowest(low, 3)
    avd = close > res[1] ? 1 : close < sup[1] ? -1 : 0;  avn = last non-zero avd
    tsl = avn == 1 ? sup : res
    crossover(close, tsl) -> entry long; else crossunder(close, tsl) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_367565_swing_stop_line_cross"
FAMILY = "donchian_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "swing": [2, 3, 5, 8],
}
DEFAULT_PARAMS = {"swing": 3}


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
    n = int(p["swing"])
    c = bars_df["close"]
    res, sup = bars_df["high"].rolling(n).max(), bars_df["low"].rolling(n).min()
    avd = np.where(c > res.shift(1), 1, np.where(c < sup.shift(1), -1, 0))
    avn = np.zeros(len(avd))
    for i in range(len(avd)):
        avn[i] = avd[i] if avd[i] != 0 else (avn[i - 1] if i else 0)
    tsl = np.where(avn == 1, sup.to_numpy(), res.to_numpy())
    cv = c.to_numpy(dtype=float)
    lag = lambda a: np.concatenate([[np.nan], a[:-1]])
    buy = (cv > tsl) & (lag(cv) <= lag(tsl))
    sell = (cv < tsl) & (lag(cv) >= lag(tsl))
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
