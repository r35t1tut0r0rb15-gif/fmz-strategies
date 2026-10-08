"""EMA 9 vs SMA 40 cross (always in): EMA 9 crossing above SMA 40 goes long, below goes short.
Port of FMZ strategy #426908 "Fast and Slow Moving Average Crossover Strategy".

Source
    https://www.fmz.com/strategy/426908 (PineScript v2/v3 syntax, FMZ last modified 2023-12-01 14:57:24).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 135-147), fast 9, slow 40
    delta = ema(close, 9) - sma(close, 40)
    crossover(delta, 0) -> entry long;  crossunder(delta, 0) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426908_ema9_sma40_cross"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 9],
    "slow": [40, 60],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 40}


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
    d = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.rolling(int(p["slow"])).mean()
    d1 = d.shift(1)
    return _always_in(((d > 0) & (d1 <= 0)).to_numpy(), ((d < 0) & (d1 >= 0)).to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
