"""Williams fractals (n = 2, equal-high tolerant) traded as written: a confirmed UP fractal (a
swing high) goes LONG, a confirmed DOWN fractal goes SHORT (always in).
Port of FMZ strategy #362418 "Smaller-Fractals-Transparency" ((Smaller) Williams Fractals).

Source
    https://www.fmz.com/strategy/362418 (PineScript v5, FMZ last modified 2022-05-11 14:11:03).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 50-99), n 2
    upFractal: high[n] above the n highs after it (strict) and above the n highs before it,
               allowing up to 4 equal highs immediately before (frontier variants 0-4)
    downFractal: mirror on lows
    upFractal -> entry long;  else downFractal -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The fractal centre is n bars back; it is known on the current bar (no lookahead).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362418_williams_fractal_side"
FAMILY = "pivot_reversal"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [2, 3, 5],
}
DEFAULT_PARAMS = {"n": 2}


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


def _fractal(x, n, up):
    v = x.to_numpy(dtype=float)
    s = 1 if up else -1                  # compare s*v so one routine handles both sides
    w = s * v
    m = len(w)
    out = np.zeros(m, dtype=bool)
    for t in range(n + n + 4, m):
        c = w[t - n]
        right = all(w[t - n + i] < c for i in range(1, n + 1))
        if not right:
            continue
        ok = False
        for k in range(5):               # 0-4 equal-or-lower bars right before the centre
            if all(w[t - n - j] <= c for j in range(1, k + 1)) and \
               all(w[t - n - i - k] < c for i in range(1, n + 1)):
                ok = True
                break
        out[t] = ok
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["n"])
    up = _fractal(bars_df["high"], n, True)
    dn = _fractal(bars_df["low"], n, False)
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
