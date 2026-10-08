"""Combo 123 Reversal & Fisher transform (HPotter): long when the 123-reversal state and the
Fisher-direction state are both +1, short when both are -1, flat otherwise.
Port of FMZ strategy #426618 "123 Reversal and Fisher Transform Indicator Combo Strategy".

Source
    https://www.fmz.com/strategy/426618 (PineScript v2/v3 syntax, FMZ last modified 2023-09-13 17:35:36).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 112-155), 15 / 1 / 3 / 50, Fisher length 10
    pos123 as HPotter's 123 reversal (stoch 15, smoothing 1 / 3, level 50)
    v1 = 0.33 * 2 * ((hl2 - lowest(hl2, 10)) / (highest - lowest) - 0.5) + 0.67 * nz(v1[1])
    v2 = clamp(v1, -0.999, 0.999 beyond +-0.99);  fish = 0.5 ln((1 + v2) / (1 - v2)) + 0.5 nz(fish[1])
    posFTI = fish > nz(fish[1]) ? 1 : fish < nz(fish[1]) ? -1 : previous
    both +1 -> entry long; both -1 -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * A flat hl2 window gives 0 / 0 = na, which propagates for that bar and restarts from nz()
      on the next, as in Pine.
    * "Trade reverse" off. strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426618_combo_123_reversal_fisher"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 15, 21],
    "length_fti": [10, 14],
}
DEFAULT_PARAMS = {"length": 15, "k_smooth": 1, "d_length": 3, "level": 50, "length_fti": 10}


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


def _state(up, dn):
    out = np.zeros(len(up))
    prev = 0.0
    for i in range(len(up)):
        prev = 1.0 if up[i] else (-1.0 if dn[i] else prev)
        out[i] = prev
    return out


def _fisher_state(bars, n):
    hl2 = (bars["high"] + bars["low"]) / 2
    mx, mn = hl2.rolling(n).max(), hl2.rolling(n).min()
    x = ((hl2 - mn) / (mx - mn)).to_numpy()
    m = len(x)
    out = np.zeros(m)
    v1p = fp = np.nan
    prev = 0.0
    with np.errstate(divide="ignore", invalid="ignore"):
        for i in range(m):
            v1 = 0.33 * 2 * (x[i] - 0.5) + 0.67 * (0.0 if np.isnan(v1p) else v1p)
            v2 = 0.999 if v1 > 0.99 else (-0.999 if v1 < -0.99 else v1)
            f = 0.5 * np.log((1 + v2) / (1 - v2)) + 0.5 * (0.0 if np.isnan(fp) else fp)
            f1 = 0.0 if np.isnan(fp) else fp
            if f > f1:
                prev = 1.0
            elif f < f1:
                prev = -1.0
            out[i] = prev
            v1p, fp = v1, f
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    lo, hi = l.rolling(n).min(), h.rolling(n).max()
    fast = (100 * (c - lo) / (hi - lo)).rolling(int(p["k_smooth"])).mean()
    slow = fast.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    a = _state(((c2 < c1) & (c > c1) & (fast < slow) & (fast > p["level"])).to_numpy(),
               ((c2 > c1) & (c < c1) & (fast > slow) & (fast < p["level"])).to_numpy())
    b = _fisher_state(bars_df, int(p["length_fti"]))
    target = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0))
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
