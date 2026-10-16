"""CCI sign, 1-hour bars: CCI 20 above zero holds a long, below zero holds a short (the default "enter ASAP" zero-line
mode).
Port of FMZ strategy #430761 "CCI Mean Reversion Channel Strategy" (CCI Strategy (REV0LUTI0N)).

FMZ source id: 430761

Source
    https://www.fmz.com/strategy/430761 (PineScript v4, FMZ last modified 2023-11-01 16:20:45).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 190-315), CCI 20, zero line; bands, confirmation, stops and time exits off
    cci > 0 -> entry long;  cci < 0 -> entry short     (every bar, "Enter First Trade ASAP" on)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Defaults: the zero-line mode with immediate entries; the band mode, the cross confirmation, the
      time-frame close and the stop / target options are off (not ported).
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, the sign of a CCI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10,000 cash per entry stored in original_sizing.txt.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430761_cci_zero_sign"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50, 100],
}
DEFAULT_PARAMS = {"length": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _cci(src, n):
    ma = src.rolling(n).mean()
    dev = src.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    return (src - ma) / (0.015 * dev.replace(0.0, np.nan))


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
    cci = _cci(bars_df["close"], int(p["length"])).to_numpy()
    m = len(cci)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if cci[i] > 0:
            pos = 1
        elif cci[i] < 0:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
