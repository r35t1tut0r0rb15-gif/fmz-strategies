"""Fractal chaos oscillator: the latest confirmed up-fractal high and down-fractal low are tracked;
a new up-fractal level goes long, a new down-fractal level goes short (always in the market).
Port of FMZ strategy #427136 "Fractal Chaos Oscillator Trading Strategy".

FMZ source id: 427136

Source
    https://www.fmz.com/strategy/427136 (PineScript v2, FMZ last modified 2023-09-18 15:10:09).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 127-163), Pattern 1, reverse off
    fractalUp: high[p+1] is a peak when high[i] < high[i+1] for i = p..1 and high[i] < high[i-1]
               for i = p+2..2p+1; the value is high[p+1] then, else the previous value (fractalDn mirrors)
    xRes = xUpper != xUpper[1] ? 1 : xLower != xLower[1] ? -1 : 0
    pos = xRes != 0 ? xRes : pos[1]; pos == 1 -> entry long; pos == -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A fractal is confirmed p bars after its peak bar: everything uses bars up to the current one.
    * Comparisons with na are false in Pine, so the first fractal value (previous value na) is not
      a change; a new fractal with the same value as the old one is not a change either (as written).
    * strategy.entry reverses: REVERSAL INTENDED; "Trade reverse" is off.
    * FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders on confirmed fractals.
    2 generic: PASS, bar counts only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: ND427136 (with #435123, Jaccard 0.743); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427136_fractal_chaos_oscillator"
FAMILY = "pivot_reversal"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pattern": [1, 2, 3],
}
DEFAULT_PARAMS = {"pattern": 1}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _fractal(x, p, up):
    """The source's fractalUp (up=True) / fractalDn on the series x, p = Pattern."""
    v = x.to_numpy(dtype=float)
    m = len(v)
    res = np.full(m, np.nan)
    for t in range(m):
        prev = res[t - 1] if t else np.nan
        res[t] = prev
        if t < 2 * p + 1:
            continue
        ok = True
        for i in range(p, 0, -1):                 # i = p .. 1: v[t-i] vs v[t-i-1]
            a, b = v[t - i], v[t - i - 1]
            if not ((a < b) if up else (a > b)):
                ok = False
        for i in range(p + 2, 2 * p + 2):         # i = p+2 .. 2p+1: v[t-i] vs v[t-i+1]
            a, b = v[t - i], v[t - i + 1]
            if not ((a < b) if up else (a > b)):
                ok = False
        if ok:
            res[t] = v[t - p - 1]
    return res


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = int({**DEFAULT_PARAMS, **params}["pattern"])
    xu = _fractal(bars_df["high"], p, True)
    xl = _fractal(bars_df["low"], p, False)
    m = len(xu)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for t in range(1, m):
        cu = not np.isnan(xu[t]) and not np.isnan(xu[t - 1]) and xu[t] != xu[t - 1]
        cl = not np.isnan(xl[t]) and not np.isnan(xl[t - 1]) and xl[t] != xl[t - 1]
        if cu:
            pos = 1
        elif cl:
            pos = -1
        tgt[t] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
