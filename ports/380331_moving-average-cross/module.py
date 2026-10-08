"""Moving average cross (Zer3192): SMA 29 crossing above SMA 69 goes long, crossing below goes short
(always in).
Port of FMZ strategy #380331 "Moving Average Cross".

Source
    https://www.fmz.com/strategy/380331 (PineScript v5, author Zer3192, FMZ last modified
    2022-08-28 07:42:12). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 45-77), slow SMA 69, fast SMA 29
    crossover(fast, slow) -> entry long;  crossunder(fast, slow) -> entry short
    close_all outside 2012-01-01 .. 2022-01-01

Interpretation choices (Pine rules in SURVEY_README.md)
    * The date range (and the close_all outside it) is a backtest window: dropped.
    * The table of per-market lengths only draws; the BTC row (44 / 13) is in the grid.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_380331_sma_29_69_cross"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [13, 29],
    "slow": [44, 69],
}
DEFAULT_PARAMS = {"fast": 29, "slow": 69}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
