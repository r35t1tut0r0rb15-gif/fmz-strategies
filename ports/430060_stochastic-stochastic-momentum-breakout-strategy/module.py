"""Stochastic pop and drop (Jake Bernstein), 4-hour bars: a 14-bar stochastic smoothed by an SMA 2 at or above 55 holds
a long, at or below 45 holds a short; between the lines the position is kept.
Port of FMZ strategy #430060 "Stochastic动量突破策略Stochastic-Momentum-Breakout-Strategy" (Pop and Drop).

FMZ source id: 430060

Source
    https://www.fmz.com/strategy/430060 (PineScript v4, FMZ last modified 2023-10-24 16:35:24).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 242-292), stochastic 14, SMA 2, lines 55 / 45
    stoch = sma(stoch(close, high, low, 14), 2)
    stoch >= 55 -> entry long;  stoch <= 45 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() line is commented out in the corpus copy; the orders are read as written (as
      #429505).
    * The 2019-2020 backtest-date block is computed but never used by any order: nothing dropped.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out cash order size stored in original_sizing.txt.
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

NAME = "fmz_430060_stochastic_pop_drop"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "osc_len": [14, 7],
    "band": [5, 10],
}
DEFAULT_PARAMS = {"osc_len": 14, "sma_len": 2, "band": 5}


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
    n = int(p["osc_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["sma_len"])).mean()
    up = (k >= 50 + p["band"]).to_numpy()
    dn = (k <= 50 - p["band"]).to_numpy()
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
