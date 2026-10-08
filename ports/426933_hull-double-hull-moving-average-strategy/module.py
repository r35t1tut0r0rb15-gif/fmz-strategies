"""Double Hull, long only: long while Hull 8 is above Hull 21; flat when below.
Port of FMZ strategy #426933 "Double HULL Moving Average Strategy".

Source
    https://www.fmz.com/strategy/426933 (PineScript v2/v3 syntax, FMZ last modified 2023-09-15 16:43:45).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 101-126), Hull 21 / 8
    hma(n) = wma(2 wma(close, round(n / 2)) - wma(close, n), round(sqrt(n)))
    hma8 > hma21 -> entry long;  hma8 < hma21 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only. FREQ = "15min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426933_double_hull_long"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pds": [5, 8],
    "pdl": [21, 34],
}
DEFAULT_PARAMS = {"pds": 8, "pdl": 21}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


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


def _hull(x, n):
    return _wma(2 * _wma(x, int(round(n / 2))) - _wma(x, n), int(round(np.sqrt(n))))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    d = _hull(c, int(p["pds"])) - _hull(c, int(p["pdl"]))
    return _long_only((d > 0).to_numpy(), (d < 0).to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
