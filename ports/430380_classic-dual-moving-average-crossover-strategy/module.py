"""Stochastic 21 / 3 / 3 turns, 4-hour bars: K crossing above D while crossing up through 14 goes long; K crossing below D
while crossing down through 86 goes short; an opposite signal while in a position closes it (the bar ends flat).
Port of FMZ strategy #430380 "Classic Dual Moving Average Crossover Strategy" (Stochastic Strategy of BiznesFilosof).

FMZ source id: 430380

Source
    https://www.fmz.com/strategy/430380 (PineScript v3, FMZ last modified 2023-10-27 16:47:30).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 209-247), stochastic 21 / 3 / 3, lines 14 / 86
    crossover(k, d) and crossover(k, 14) -> entry long;  crossunder(k, d) and crossunder(k, 86) -> entry short
    short signal and long -> close_all;  long signal and short -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close_all is written after the opposite entry on the same bar; it acts on the position held
      at the start of the bar and the bar ends flat (the convention used for close_all after an entry
      in these ports), so a signal against a position flattens it and the next signal from flat opens
      the new side.
    * The strategy() line is commented out in the corpus copy: orders read as written (as #429505).
      The 2011-2050 window is unused (window = true). FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out 20 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430380_stochastic_biznesfilosof"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 14],
    "bottom": [14, 20],
}
DEFAULT_PARAMS = {"length": 21, "smooth_k": 3, "smooth_d": 3, "bottom": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    b, u = float(p["bottom"]), 100 - float(p["bottom"])
    lsig = ((k > d) & (k.shift(1) <= d.shift(1)) & (k > b) & (k.shift(1) <= b)).to_numpy()
    ssig = ((k < d) & (k.shift(1) >= d.shift(1)) & (k < u) & (k.shift(1) >= u)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 0:
            pos = 1 if lsig[i] else (-1 if ssig[i] else 0)
        elif pos == 1 and ssig[i]:
            pos = 0
        elif pos == -1 and lsig[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
