"""Ichimoku cloud breaks (HPotter), 1-hour bars: a close under the 52-bar channel midpoint of 26 bars ago holds a short, a
close over the average of the Tenkan and Kijun of 26 bars ago holds a long.
Port of FMZ strategy #430570 "Ichimoku Equilibrium Strategy" (Ichimoku2c Backtest).

FMZ source id: 430570

Source
    https://www.fmz.com/strategy/430570 (PineScript v2, FMZ last modified 2023-10-30 14:45:40).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 162-199), conversion 9, base 26, span 52, displacement 26
    Tenkan = mid(9); Kijun = mid(26); SenkouA = mid(52); SenkouB = (Tenkan[26] + Kijun[26]) / 2   (mid = Donchian midpoint)
    close < SenkouA[26] -> -1 (entry short);  close > SenkouB -> 1 (entry long);  else pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * The span names are swapped against the usual Ichimoku ones in the source; kept as written.
      Both spans use only bars already closed (26 bars back).
    * "Trade reverse" defaults to false and is fixed. strategy.entry reverses: REVERSAL INTENDED.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel midpoints.
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

NAME = "fmz_430570_ichimoku2c"
FAMILY = "ichimoku"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "span": [52, 26],
    "displacement": [26, 13],
}
DEFAULT_PARAMS = {"conversion": 9, "base": 26, "span": 52, "displacement": 26}


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
    mid = lambda n: (lo.rolling(n).min() + h.rolling(n).max()) / 2  # noqa: E731
    tenkan, kijun, span_a = mid(int(p["conversion"])), mid(int(p["base"])), mid(int(p["span"]))
    b = int(p["base"])
    span_b = (tenkan.shift(b) + kijun.shift(b)) / 2
    dn = (c < span_a.shift(int(p["displacement"]))).to_numpy()
    up = (c > span_b).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if dn[i]:
            pos = -1
        elif up[i]:
            pos = 1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
