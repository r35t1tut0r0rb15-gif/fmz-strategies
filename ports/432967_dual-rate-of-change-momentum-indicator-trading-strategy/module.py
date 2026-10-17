"""HPotter MovROC (Pring's KST), 1-hour bars: the weighted sum of four smoothed rates of change (6 / 10 / 15 / 20 bars,
smoothed 10 / 10 / 9 / 15, weights 1-4) above zero turns the state long, below zero short; always in the state's
direction.
Port of FMZ strategy #432967 "Dual Rate of Change Momentum Indicator Trading Strategy" (MovROC (KST indicator)).

FMZ source id: 432967

Source
    https://www.fmz.com/strategy/432967 (PineScript v2, FMZ last modified 2023-11-23 10:37:00).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 145-160), ROC 6 / 10 / 15 / 20, SMA 10 / 10 / 9 / 15, reverse false
    nRes = sma(roc(close, 6), 10) + 2 sma(roc(close, 10), 10) + 3 sma(roc(close, 15), 9) + 4 sma(roc(close, 20), 15)
    pos = nRes > 0 ? 1 : nRes < 0 ? -1 : nz(pos[1], 0);  pos 1 -> entry long;  pos -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * roc() is 100 x (close - close[n]) / close[n]. The state holds at exactly zero.
    * strategy.entry reverses: REVERSAL INTENDED. reverse is false. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, rates of change in percent.
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

NAME = "fmz_432967_movroc_kst_state"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "roc1": [6, 4],
    "roc4": [20, 30],
}
DEFAULT_PARAMS = {"roc1": 6, "roc2": 10, "roc3": 15, "roc4": 20, "sm1": 10, "sm2": 10, "sm3": 9, "sm4": 15}


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
    c = bars_df["close"]

    def sroc(n, s):
        cn = c.shift(int(n))
        return (100 * (c - cn) / cn).rolling(int(s)).mean()

    res = (sroc(p["roc1"], p["sm1"]) + 2 * sroc(p["roc2"], p["sm2"]) + 3 * sroc(p["roc3"], p["sm3"])
           + 4 * sroc(p["roc4"], p["sm4"])).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if res[i] > 0:
            pos = 1
        elif res[i] < 0:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    se = (tgt == -1) & (prev != -1)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, false, se, false.copy()))


def portfolio_kwargs(**params):
    return {}
