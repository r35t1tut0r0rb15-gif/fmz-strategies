"""Six nested three-bar harmonic means of the previous closes, 2-hour bars: the lowest of the first three crossing over the highest of the last three goes long; the lower of the first two crossing under the
higher of the third and fourth goes short; reversing.
Port of FMZ strategy #442520 "Harmonic Dual System Strategy" (Harmonic System Strategy).

FMZ source id: 442520

Source
    https://www.fmz.com/strategy/442520 (PineScript v4, FMZ last modified 2024-02-22 15:49:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 124-158), no inputs
    T1 = harm(close[1], close[2], close[3]);  Tk = harm(T(k-1), T(k-1)[1], T(k-1)[2]), k = 2 .. 6
    crossover(min(T1, T2, T3), max(T4, T5, T6)) -> entry Long;  crossunder(min(T1, T2), max(T3, T4)) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * T1 starts from the previous close, as written. The Balance line only plots. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, harmonic-mean ladder crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442520_harmonic_mean_ladder_cross_reversal"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _harm(x, y, z):
    return 3.0 / (1.0 / x + 1.0 / y + 1.0 / z)


def simulate(bars_df, **params):
    c = bars_df["close"]
    t = [_harm(c.shift(1), c.shift(2), c.shift(3))]
    for _ in range(5):
        prev = t[-1]
        t.append(_harm(prev, prev.shift(1), prev.shift(2)))
    t1, t2, t3, t4, t5, t6 = t
    x1 = pd.concat([t1, t2, t3], axis=1).min(axis=1, skipna=False)
    x2 = pd.concat([t4, t5, t6], axis=1).max(axis=1, skipna=False)
    x3 = pd.concat([t1, t2], axis=1).min(axis=1, skipna=False)
    x4 = pd.concat([t3, t4], axis=1).max(axis=1, skipna=False)
    le = (x1 > x2) & (x1.shift(1) <= x2.shift(1))
    se = (x3 < x4) & (x3.shift(1) >= x4.shift(1))
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
