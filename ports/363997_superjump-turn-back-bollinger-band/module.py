"""SuperJump turn-back Bollinger: the open crossing back above the lower band (SMA 68 of opens
- 2 sd) on an up bar goes long; crossing back below the upper band on a down bar goes short.
Port of FMZ strategy #363997 "SuperJump Turn Back Bollinger Band".

Source
    https://www.fmz.com/strategy/363997 (PineScript v5, FMZ last modified 2022-05-18 11:27:17).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 53-118), length 68, source open, StdDev 2
    LongSig  = crossunder(lower, open) and close > open
    ShortSig = crossover(upper, open) and close < open
    LongSig -> entry long; else ShortSig -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * crossunder(lower, open) = open crossing above the lower band. Population stdev.
    * The wide (2.5 sd) band and the ATR stop only feed alerts and plots; not ported.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_363997_bollinger_turn_back"
FAMILY = "bollinger_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40, 68],
    "mult": [1.5, 2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 68, "mult": 2.0}


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
    o, c = bars_df["open"], bars_df["close"]
    n = int(p["length"])
    basis, sd = o.rolling(n).mean(), o.rolling(n).std(ddof=0)
    upper, lower = basis + p["mult"] * sd, basis - p["mult"] * sd
    long_ = ((lower < o) & (lower.shift(1) >= o.shift(1)) & (c > o)).to_numpy()
    short = ((upper > o) & (upper.shift(1) <= o.shift(1)) & (c < o)).to_numpy()
    return _always_in(long_, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
