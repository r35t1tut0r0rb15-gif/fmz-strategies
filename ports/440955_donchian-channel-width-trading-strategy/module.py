"""Donchian width regime, 1-hour bars: the 50-bar channel width under its 50-bar SMA goes long, above it short; reversing.
Port of FMZ strategy #440955 "Donchian Channel Width Trading Strategy" (Donchian Channel Width Strategy).

FMZ source id: 440955

Source
    https://www.fmz.com/strategy/440955 (PineScript v2, FMZ last modified 2024-02-04 10:35:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 176-194), length 50, smoothing 50; reverse off
    width = highest(high, 50) - lowest(low, 50);  pos = width > sma(width, 50) ? -1 : width < sma(width, 50) ? 1 : pos[1];  1 -> entry Long, -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state is a level (a narrowing channel is long, a widening one short, as written).
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel width against its average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440955_donchian_width_regime"
FAMILY = "volatility_regime"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 20],
    "smoothe": [50, 20],
}
DEFAULT_PARAMS = {"length": 50, "smoothe": 50, "reverse": False}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    w = bars_df["high"].rolling(n).max() - bars_df["low"].rolling(n).min()
    s = w.rolling(int(p["smoothe"])).mean()
    wide, narrow = (w > s).to_numpy(), (w < s).to_numpy()
    m = len(w)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if wide[i]:
            pos = -1
        elif narrow[i]:
            pos = 1
        tgt[i] = pos
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
