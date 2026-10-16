"""Pring's Special K (HPotter), 1-hour bars: the weighted sum of twelve smoothed rates of change above its SMA 10 holds a
long, below it holds a short.
Port of FMZ strategy #430285 "Momentum Stacking Strategy of Different Timeframes" (Martin Pring's Special K Backtest).

FMZ source id: 430285

Source
    https://www.fmz.com/strategy/430285 (PineScript v2, FMZ last modified 2023-10-26 17:39:26).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 142-182), ROC 10-530 with smoothing 10-195 and weights 1-4, signal SMA 10
    osc = sum of w x sma(roc(close, n), s) over (n, s, w) = (10,10,1) (15,10,2) (20,10,3) (30,15,4) (40,50,1) (65,65,2)
          (75,75,3) (100,100,4) (195,130,1) (265,130,2) (390,130,3) (530,195,4)
    osc > sma(osc, 10) -> entry long;  osc < sma(osc, 10) -> entry short;  else pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * roc is the percentage change over n bars. "Trade reverse" defaults to false and is fixed.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, rates of change.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_430285_pring_special_k"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "smooth": [10, 5, 20],
}
DEFAULT_PARAMS = {"smooth": 10}
TERMS = ((10, 10, 1), (15, 10, 2), (20, 10, 3), (30, 15, 4), (40, 50, 1), (65, 65, 2), (75, 75, 3), (100, 100, 4),
         (195, 130, 1), (265, 130, 2), (390, 130, 3), (530, 195, 4))


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
    osc = None
    for n, s, w in TERMS:
        term = (100 * (c - c.shift(n)) / c.shift(n)).rolling(s).mean() * w
        osc = term if osc is None else osc + term
    sig = osc.rolling(int(p["smooth"])).mean()
    up, dn = (osc > sig).to_numpy(), (osc < sig).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
