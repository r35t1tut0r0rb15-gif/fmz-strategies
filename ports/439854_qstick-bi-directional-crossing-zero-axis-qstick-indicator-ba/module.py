"""Chande's Qstick, 1-hour bars: a 14-bar average of close minus open above zero holds a long, below zero a short; reversing; the entry is sent on every bar of the state.
Port of FMZ strategy #439854 "双向交叉零轴Qstick指标回测策略Bi-directional-Crossing-Zero-Axis-Qstick-Indicator-Backtest-Strategy" (Qstick Indicator Backtest).

FMZ source id: 439854

Source
    https://www.fmz.com/strategy/439854 (PineScript v2, FMZ last modified 2024-01-24 14:14:07).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 141-179), length 14; reverse off
    xQstick = sma(close - open, 14);  pos = xQstick > 0 ? 1 : xQstick < 0 ? -1 : previous (0);  possig 1 -> entry Long, -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A same-side entry while in the position is ignored. strategy.entry reverses: REVERSAL INTENDED. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average candle body sign.
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

NAME = "fmz_439854_hpotter_qstick_zero_state"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 30, 7],
}
DEFAULT_PARAMS = {"length": 14}


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
    q = (bars_df["close"] - bars_df["open"]).rolling(int(p["length"])).mean().to_numpy()
    m = len(q)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if q[i] > 0:
            pos = 1
        elif q[i] < 0:
            pos = -1
        tgt[i] = pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(tgt == 1, index=ix), false, pd.Series(tgt == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
