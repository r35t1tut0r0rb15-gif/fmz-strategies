"""MACD cross with divergence against the previous cross: long on a golden cross whose close is
below but whose MACD line is above the values at the previous golden cross; short mirror.
Port of FMZ strategy #362060 "tv高低点策略" ([blackcat] L2 Reversal Labels, orders added).

Source
    https://www.fmz.com/strategy/362060 (PineScript v4, author "Zer3192", FMZ last modified
    2022-05-27 05:34:08). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 37-59), MACD 12/26/9
    a1 = barssince(crossover(diff,dea)[1]); a2 = barssince(crossunder(diff,dea)[1])
    bottom = close[a1+1] > close and diff > diff[a1+1] and crossover(diff, dea)
    top    = close[a2+1] < close and diff[a2+1] > diff and crossunder(diff, dea)
    bottom -> entry long;  else top -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * close[a1+1] is the close on the bar of the previous golden cross (before this bar);
      no previous cross -> no signal.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362060_macd_cross_divergence"
FAMILY = "macd_divergence"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 12],
    "slow": [21, 26, 34],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


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
    diff = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    dea = diff.ewm(span=int(p["signal"]), adjust=False).mean()
    xo = ((diff > dea) & (diff.shift(1) <= dea.shift(1))).to_numpy()
    xu = ((diff < dea) & (diff.shift(1) >= dea.shift(1))).to_numpy()
    cv, dv = c.to_numpy(dtype=float), diff.to_numpy()
    m = len(cv)
    bottom, top = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last_xo = last_xu = -1
    warm = int(p["slow"])
    for t in range(m):
        if t >= warm:
            if xo[t] and last_xo >= 0 and cv[last_xo] > cv[t] and dv[t] > dv[last_xo]:
                bottom[t] = True
            if xu[t] and last_xu >= 0 and cv[last_xu] < cv[t] and dv[last_xu] > dv[t]:
                top[t] = True
        if xo[t]:
            last_xo = t
        if xu[t]:
            last_xu = t
    return _always_in(bottom, top, bars_df.index)


def portfolio_kwargs(**params):
    return {}
