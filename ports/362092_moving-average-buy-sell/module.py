"""EMA 20 / EMA 200 cross, stop-and-reverse ("Moving Average Buy-Sell").
Port of FMZ strategy #362092 "Moving-Average-Buy-Sell".

Source
    https://www.fmz.com/strategy/362092 (PineScript v5, FMZ last modified 2022-05-09 23:46:33).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 47-75)
    Wave = ema(close,20); Tide = ema(close,200)
    crossover(Wave, Tide) -> entry long;  else crossover(Tide, Wave) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362092_ema_20_200_cross"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "wave": [10, 20, 50],
    "tide": [100, 200],
}
DEFAULT_PARAMS = {"wave": 20, "tide": 200}


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
    w = c.ewm(span=int(p["wave"]), adjust=False).mean()
    t = c.ewm(span=int(p["tide"]), adjust=False).mean()
    warm = np.arange(len(c)) >= int(p["wave"])
    up = ((w > t) & (w.shift(1) <= t.shift(1))).to_numpy() & warm
    dn = ((t > w) & (t.shift(1) <= w.shift(1))).to_numpy() & warm
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
