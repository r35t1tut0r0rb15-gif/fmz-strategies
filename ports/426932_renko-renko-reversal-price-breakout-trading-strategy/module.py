"""Four-bar reversal (always in): a red bar followed by four green bars goes long; a green bar
followed by four red bars goes short.
Port of FMZ strategy #426932 "Renko Reversal Price Breakout Trading Strategy".

Source
    https://www.fmz.com/strategy/426932 (PineScript v2/v3 syntax, FMZ last modified 2023-09-15 16:27:29).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 83-91)
    buy  = close[4] < open[4] and close[3..0] > open[3..0]
    sell = close[4] > open[4] and close[3..0] < open[3..0]

Interpretation choices (Pine rules in SURVEY_README.md)
    * Despite the title the script runs on ordinary candles (no Renko source); ported as coded.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}). Qty 1 is sizing.
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426932_four_bar_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "run": [3, 4, 5],
}
DEFAULT_PARAMS = {"run": 4}


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
    k = int(p["run"])
    green = bars_df["close"] > bars_df["open"]
    red = bars_df["close"] < bars_df["open"]
    g_run = green.astype(float).rolling(k).sum() == k
    r_run = red.astype(float).rolling(k).sum() == k
    buy = (red.shift(k, fill_value=False) & g_run).to_numpy()
    sell = (green.shift(k, fill_value=False) & r_run).to_numpy()
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
