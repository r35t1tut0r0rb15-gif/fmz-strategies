"""Ehlers bandpass filter of hl2, reversed, 1-hour bars: a filter value above zero holds a short, at or below zero a long; reversing; the entry is sent on every bar of the state.
Port of FMZ strategy #439878 "Bandpass Filter Reversed Strategy" (Bandpass Filter Reversed Strategy).

FMZ source id: 439878

Source
    https://www.fmz.com/strategy/439878 (PineScript v2, FMZ last modified 2024-01-24 15:28:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 163-188), length 20; delta 0.5; trigger level 0
    beta = cos(3.14 x (360 / L) / 180);  gamma = 1 / cos(3.14 x (720 x delta / L) / 180);  alpha = gamma - sqrt(gamma^2 - 1)
    BP = 0.5 (1 - alpha)(hl2 - hl2[2]) + beta (1 + alpha) nz(BP[1]) - alpha nz(BP[2]);  pos = BP > 0 ? -1 : BP <= 0 ? 1 : previous

Interpretation choices (Pine rules in SURVEY_README.md)
    * The angles use 3.14 and degree conversion, as written. The filter starts from zero history (nz).
      A same-side entry while in the position is ignored. strategy.entry reverses: REVERSAL INTENDED.
      No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bandpass filter sign.
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

NAME = "fmz_439878_hpotter_bandpass_reversed_state"
FAMILY = "cycle_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "delta": [0.5, 0.25],
}
DEFAULT_PARAMS = {"length": 20, "delta": 0.5, "trigger": 0.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    hl2 = ((bars_df["high"] + bars_df["low"]) / 2).to_numpy(dtype=float)
    n, dl = int(p["length"]), float(p["delta"])
    beta = np.cos(3.14 * (360 / n) / 180)
    gamma = 1 / np.cos(3.14 * (720 * dl / n) / 180)
    alpha = gamma - np.sqrt(gamma * gamma - 1)
    m = len(hl2)
    bp = np.full(m, np.nan)
    for i in range(2, m):
        b1 = bp[i - 1] if not np.isnan(bp[i - 1]) else 0.0
        b2 = bp[i - 2] if not np.isnan(bp[i - 2]) else 0.0
        bp[i] = 0.5 * (1 - alpha) * (hl2[i] - hl2[i - 2]) + beta * (1 + alpha) * b1 - alpha * b2
    trg = float(p["trigger"])
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if bp[i] > trg:
            pos = -1
        elif bp[i] <= trg:
            pos = 1
        tgt[i] = pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(tgt == 1, index=ix), false, pd.Series(tgt == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
