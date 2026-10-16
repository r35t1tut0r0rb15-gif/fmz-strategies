"""Chande momentum (HPotter's form), 1-hour bars: the 9-bar net change over the sum of absolute changes, x100, above 70
holds a long, at or below -70 holds a short.
Port of FMZ strategy #430117 "Momentum Arbitrage Strategy Backtest Analysis" (CMO (Chande Momentum Oscillator)).

FMZ source id: 430117

Source
    https://www.fmz.com/strategy/430117 (PineScript v2, FMZ last modified 2023-10-25 11:10:59).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 176-219), length 9, bands 70 / -70
    nRes = 100 x (close - close[9]) / (sma(|close - close[1]|, 9) x 9)
    nRes > 70 -> entry long;  nRes <= -70 -> entry short;  else pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Trade reverse" defaults to false and is fixed. strategy.entry reverses: REVERSAL INTENDED.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a bounded momentum oscillator.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: ND430117 (4 members, best partner #442108, Jaccard 0.737); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430117_cmo_bands"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [9, 14, 20],
    "band": [70, 50],
}
DEFAULT_PARAMS = {"length": 9, "band": 70}


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
    n = int(p["length"])
    den = (c.diff().abs().rolling(n).mean() * n).replace(0.0, np.nan)
    res = (100 * (c - c.shift(n)) / den).to_numpy()
    b = float(p["band"])
    m = len(res)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if res[i] > b:
            pos = 1
        elif res[i] <= -b:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
