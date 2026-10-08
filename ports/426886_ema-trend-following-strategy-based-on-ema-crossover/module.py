"""EMA cross of hl2 (always in): EMA 20 crossing above EMA 60 goes long, crossing below goes short.
Port of FMZ strategy #426886 "EMA Trend Following Strategy Based on EMA Crossover".

Source
    https://www.fmz.com/strategy/426886 (PineScript v4, FMZ last modified 2023-09-15 11:51:34).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 154-187), length 20, ratio 3, long only off
    fast = ema(hl2, 20); slow = ema(hl2, 60)
    crossover(fast, slow) -> entry long;  crossunder(fast, slow) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * With "Long Only" off the long close never fires and shorts reverse: REVERSAL INTENDED.
    * The start year (2020) is a backtest window: dropped.
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426886_hl2_ema_cross"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20, 30],
    "ratio": [3, 5],
}
DEFAULT_PARAMS = {"length": 20, "ratio": 3}


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
    hl2 = (bars_df["high"] + bars_df["low"]) / 2
    n = int(p["length"])
    d = hl2.ewm(span=n, adjust=False).mean() - hl2.ewm(span=n * int(p["ratio"]), adjust=False).mean()
    d1 = d.shift(1)
    return _always_in(((d > 0) & (d1 <= 0)).to_numpy(), ((d < 0) & (d1 >= 0)).to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
