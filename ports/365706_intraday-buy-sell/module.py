"""Intraday BUY/SELL: a green bar that closed above SMA 50 (crossing it) followed by a green bar
with a higher high goes long; a red bar whose low crossed below the SMA followed by a red bar with
a lower low goes short (always in).
Port of FMZ strategy #365706 "CRUDE OIL BUY/SELL".

Source
    https://www.fmz.com/strategy/365706 (PineScript v4, FMZ last modified 2022-05-25 17:44:23).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 51-102), SMA 50
    BUY  = crossover(close[1], sma) and close[1] > open[1] and high > high[1] and close > open
    SELL = crossunder(low[1], sma) and close[1] < open[1] and low < low[1] and close < open
    BUY -> entry long; else SELL -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * crossover(close[1], sma) compares close[1] with the current SMA and close[2] with sma[1],
      as coded.
    * The RSI reversal markers and colour rules only draw.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365706_sma_cross_followthrough"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [20, 50, 100],
}
DEFAULT_PARAMS = {"sma_len": 50}


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
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    sma = c.rolling(int(p["sma_len"])).mean()
    c1, l1 = c.shift(1), l.shift(1)
    buy = ((c1 > sma) & (c.shift(2) <= sma.shift(1)) & (c1 > o.shift(1)) & (h > h.shift(1)) & (c > o)).to_numpy()
    sell = ((l1 < sma) & (l.shift(2) >= sma.shift(1)) & (c1 < o.shift(1)) & (l < l1) & (c < o)).to_numpy()
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
