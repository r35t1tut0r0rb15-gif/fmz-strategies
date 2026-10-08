"""Two SMA crosses (always in): SMA 5 crossing above SMA 21 goes long; SMA 14 crossing under SMA 28
goes short.
Port of FMZ strategy #426776 "Moving Average Crossover Strategy".

Source
    https://www.fmz.com/strategy/426776 (PineScript v2/v3 syntax, FMZ last modified 2023-09-14 14:55:49).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 104-110)
    crossover(sma(close, 5), sma(close, 21))   -> entry long
    crossunder(sma(close, 14), sma(close, 28)) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both crosses can fall on one bar: both orders fill at the next open in source order and the
      later short stands (short_first).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "2h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426776_two_sma_crosses"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "long_pair": [(5, 21), (10, 30)],
    "short_pair": [(14, 28), (10, 30)],
}
DEFAULT_PARAMS = {"long_pair": (5, 21), "short_pair": (14, 28)}


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
    sma = lambda n: c.rolling(int(n)).mean()
    a = sma(p["long_pair"][0]) - sma(p["long_pair"][1])
    b = sma(p["short_pair"][0]) - sma(p["short_pair"][1])
    long_ = ((a > 0) & (a.shift(1) <= 0)).to_numpy()
    short = ((b < 0) & (b.shift(1) >= 0)).to_numpy()
    return _always_in(long_, short, bars_df.index, short_first=True)


def portfolio_kwargs(**params):
    return {}
