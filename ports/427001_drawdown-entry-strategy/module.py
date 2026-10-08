"""Noro's drawdown entry, long only: a close more than 5 % under the last up-close goes long; a green
bar while long closes it.
Port of FMZ strategy #427001 "Drawdown Entry Strategy".

Source
    https://www.fmz.com/strategy/427001 (PineScript v2/v3 syntax, FMZ last modified 2023-09-16 19:18:38).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 144-158), drawdown -5 %
    lastbull = close > close[1] ? close : lastbull[1]
    dd = (close / lastbull - 1) * 100;  dd < -5 -> entry long
    long and close > open -> entry "Close" short with qty 0 (an exit)

Interpretation choices (Pine rules in SURVEY_README.md)
    * A qty-0 short entry is an exit (Noro's idiom). The exit tests the position at the close:
      from flat a signal bar's entry stands; while long the exit goes flat. Long only.
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427001_noro_drawdown_long"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "signal": [-3.0, -5.0, -8.0],
}
DEFAULT_PARAMS = {"signal": -5.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(target, index):
    """Signals from the position each bar's orders leave (1 / 0 / -1): a change to +-1 is an
    entry (reversing an opposite position), a change to 0 an exit of the side held."""
    m = len(target)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    prev = 0
    for i in range(m):
        n = target[i]
        if n != prev:
            if n == 1:
                le[i] = True
            elif n == -1:
                se[i] = True
            elif prev == 1:
                lx[i] = True
            else:
                sx[i] = True
        prev = n
    return tuple(pd.Series(x, index=index) for x in (le, lx, se, sx))


def _long_only(entry, out, index):
    """Pine order for a long-only script: an entry from flat stands (a close finds no position at
    the close); while long the entry is refused and the close goes flat."""
    target = np.zeros(len(entry), dtype=int)
    pos = 0
    for i in range(len(entry)):
        if pos == 0 and entry[i]:
            pos = 1
        elif pos == 1 and out[i]:
            pos = 0
        target[i] = pos
    return _emit(target, index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    cv = c.to_numpy(dtype=float)
    last = np.full(len(cv), np.nan)
    prev = np.nan
    for i in range(len(cv)):
        if i > 0 and cv[i] > cv[i - 1]:
            prev = cv[i]
        last[i] = prev
    dd = (cv / last - 1) * 100
    entry = dd < p["signal"]
    return _long_only(entry, (c > o).to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
