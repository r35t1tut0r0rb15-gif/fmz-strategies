"""HPotter DiNapoli detrended oscillator, reversed (the source default): the close above its SMA 14 holds
a short, at or below it a long (always in the market once the SMA exists).
Port of FMZ strategy #427679 "DiNapoli Detrended Oscillator Strategy".

FMZ source id: 427679

Source
    https://www.fmz.com/strategy/427679 (PineScript v2, FMZ last modified 2023-09-23 15:48:40).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 217-238), length 14, trigger 0, reverse TRUE
    nRes = close - sma(close, 14); pos = nRes > 0 ? 1 : nRes <= 0 ? -1 : nz(pos[1], 0)
    possig = reverse ? -pos : pos -> entry long / entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Trade reverse" defaults to TRUE in the source and is kept (fixed, not searched).
    * pos is 0 (no order) while the SMA is na.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close minus its average, zero trigger.
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

NAME = "fmz_427679_hpotter_dinapoli_detrended_rev"
FAMILY = "mean_reversion_band"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7, 28, 50],
}
DEFAULT_PARAMS = {"length": 14, "trigger": 0.0, "reverse": True}


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
    c = bars_df["close"]
    res = (c - c.rolling(int(p["length"])).mean()).to_numpy()
    m = len(res)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if res[i] > p["trigger"]:
            pos = 1
        elif res[i] <= p["trigger"]:
            pos = -1
        tgt[i] = -pos if p["reverse"] else pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
