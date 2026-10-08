"""NR7 inside-day long (ChartArt): a green inside bar that is also the narrowest of 7, with SMA 14
rising, goes long; the next green bar closes it.
Port of FMZ strategy #426905 "Narrow Range Inside Day Breakout Strategy".

Source
    https://www.fmz.com/strategy/426905 (PineScript v2/v3 syntax, FMZ last modified 2023-12-01 15:00:06).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 166-196), SMA 14
    nr7 and inside and open < close and change(sma(close, 14)) > 0 -> entry long
    open < close -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry bar is green too: at that close no position exists, so the close does nothing
      and the long stands until the next green bar. Long only (mirror of #426812).
    * FREQ = "10min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426905_nr7_inside_day_long"
FAMILY = "candle_pattern"  # proposed 2026-10-07, user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "nr_bars": [4, 7],
    "ma_length": [14, 28],
}
DEFAULT_PARAMS = {"nr_bars": 7, "ma_length": 14}


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
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    rng = h - l
    nr = pd.Series(True, index=bars_df.index)
    for k in range(1, int(p["nr_bars"])):
        nr &= rng < rng.shift(k)
    inside = (h < h.shift(1)) & (l > l.shift(1))
    rising = c.rolling(int(p["ma_length"])).mean().diff() > 0
    green = (o < c)
    entry = (nr & inside & green & rising).to_numpy()
    return _long_only(entry, green.to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
