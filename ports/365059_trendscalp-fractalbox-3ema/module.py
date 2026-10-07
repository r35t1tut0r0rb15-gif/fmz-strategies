"""Fractal box: a close above the last Williams-style fractal high level goes long; a close below
the last fractal low level goes short (always in). The EMA ribbon only draws.
Port of FMZ strategy #365059 "[VDB]TrendScalp-FractalBox-3EMA".

Source
    https://www.fmz.com/strategy/365059 (PineScript v5, FMZ last modified 2022-05-23 12:01:38).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 125-153)
    fractHigh = high[4] <= high[2] and high[3] <= high[2] and high[2] > high[1] and high[2] > high
    fractLevelHigh := fractHigh ? high[2] : nz(fractLevelHigh[1], high)   (low mirrors)
    close > fractLevelHigh -> entry long; else close < fractLevelLow -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The fractal is confirmed two bars after its centre (no look-ahead); before the first
      fractal the level is the bar's own high / low (nz), as coded.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "45min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365059_fractal_box_breakout"
FAMILY = "pivot_reversal"  # proposed 2026-10-07, user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    h, l, c = (bars_df[k] for k in ("high", "low", "close"))
    f_hi = ((h.shift(4) <= h.shift(2)) & (h.shift(3) <= h.shift(2)) & (h.shift(2) > h.shift(1)) & (h.shift(2) > h)).to_numpy()
    f_lo = ((l.shift(4) >= l.shift(2)) & (l.shift(3) >= l.shift(2)) & (l.shift(2) < l.shift(1)) & (l.shift(2) < l)).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), l.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    lvl_h, lvl_l = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        ph = lvl_h[i - 1] if i else np.nan
        pl = lvl_l[i - 1] if i else np.nan
        lvl_h[i] = hv[i - 2] if f_hi[i] else (hv[i] if np.isnan(ph) else ph)
        lvl_l[i] = lv[i - 2] if f_lo[i] else (lv[i] if np.isnan(pl) else pl)
    return _always_in(cv > lvl_h, cv < lvl_l, bars_df.index)


def portfolio_kwargs(**params):
    return {}
