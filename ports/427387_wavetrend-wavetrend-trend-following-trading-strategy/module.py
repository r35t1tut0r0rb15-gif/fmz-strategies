"""Noro's WaveTrend v1.0, long only by default: the WaveTrend line (EMA 21 of the channel index of
hlc3, 10) turning positive goes long; turning negative closes the long (the short side is off).
Port of FMZ strategy #427387 "WaveTrend Trend Following Trading Strategy".

FMZ source id: 427387

Source
    https://www.fmz.com/strategy/427387 (PineScript v2, FMZ last modified 2023-09-20 15:50:08).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 165-199), only long on
    esa = ema(hlc3, 10); d = ema(|hlc3 - esa|, 10); ci = (hlc3 - esa) / (0.015 d); tci = ema(ci, 21)
    posi = tci > 0 ? 1 : tci < 0 ? -1 : posi[1]
    posi turns 1 -> entry long; posi turns -1 -> entry short with qty 0 (only long) = close long

Interpretation choices (Pine rules in SURVEY_README.md; Noro's idiom as worker A's ports)
    * "Only Long" is on: the short entry has qty 0 and only closes the long. The grid also tries
      both sides (`only_long` False), where the turns reverse (REVERSAL INTENDED).
    * FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a normalised channel index.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only by default; REVERSAL INTENDED with both sides on.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427387_noro_wavetrend"
FAMILY = "wavetrend_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "channel": [10, 20],
    "average": [21, 40],
    "only_long": [True, False],
}
DEFAULT_PARAMS = {"channel": 10, "average": 21, "only_long": True}


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
    n1, n2 = int(p["channel"]), int(p["average"])
    hlc3 = (bars_df["high"] + bars_df["low"] + bars_df["close"]) / 3
    esa = hlc3.ewm(span=n1, adjust=False).mean()
    d = (hlc3 - esa).abs().ewm(span=n1, adjust=False).mean()
    tci = ((hlc3 - esa) / (0.015 * d)).ewm(span=n2, adjust=False).mean().to_numpy()
    only_long = bool(p["only_long"])
    m = len(tci)
    tgt = np.zeros(m, dtype=np.int8)
    posi, prev_posi, pos = 0, 0, 0
    for i in range(m):
        if tci[i] > 0:
            posi = 1
        elif tci[i] < 0:
            posi = -1
        if posi == 1 and prev_posi < 1:
            pos = 1
        elif posi == -1 and prev_posi > -1:
            pos = 0 if only_long else -1
        prev_posi = posi
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
