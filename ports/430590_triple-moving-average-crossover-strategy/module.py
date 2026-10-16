"""Bill Williams' three displaced lines (HPotter), 1-hour bars: the close below the SMA 5 (shifted 3) below the SMA 8
(shifted 5) below the SMA 13 (shifted 8) of hl2 holds a short; the mirror stack holds a long.
Port of FMZ strategy #430590 "Triple Moving Average Crossover Strategy" (Bill Williams Averages. 3Lines).

FMZ source id: 430590

Source
    https://www.fmz.com/strategy/430590 (PineScript v2, FMZ last modified 2023-10-30 16:38:01).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 147-178), SMA 13 / 8 / 5 of hl2, displacements 8 / 5 / 3
    L = sma(hl2, 13)[8]; M = sma(hl2, 8)[5]; S = sma(hl2, 5)[3]
    close < S < M < L -> -1;  close > S > M > L -> 1;  else pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * The displacements read past values ([n]), so no future data. "Trade reverse" defaults to false
      and is fixed. strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, displaced moving averages.
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

NAME = "fmz_430590_williams_three_lines"
FAMILY = "alligator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "l_length": [13, 21],
    "l_offset": [8, 5],
}
DEFAULT_PARAMS = {"l_length": 13, "m_length": 8, "s_length": 5, "l_offset": 8, "m_offset": 5, "s_offset": 3}


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
    hl2 = (bars_df["high"] + bars_df["low"]) / 2
    c = bars_df["close"]
    L = hl2.rolling(int(p["l_length"])).mean().shift(int(p["l_offset"]))
    M = hl2.rolling(int(p["m_length"])).mean().shift(int(p["m_offset"]))
    S = hl2.rolling(int(p["s_length"])).mean().shift(int(p["s_offset"]))
    dn = ((c < S) & (S < M) & (M < L)).to_numpy()
    up = ((c > S) & (S > M) & (M > L)).to_numpy()
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
