"""Three SMA correction system, 2-hour bars: SMA 9 above SMA 18 with SMA 4 rising goes long (when not
long); SMA 9 below SMA 18 with SMA 4 falling turns a long into a short (shorts only open from a long).
Port of FMZ strategy #428089 "Triple Moving Average Crossover System".

FMZ source id: 428089

Source
    https://www.fmz.com/strategy/428089 (PineScript v4, FMZ last modified 2023-09-28 15:33:14).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 163-186), SMA 18 / 9 / 4
    sma9 > sma18 and sma4 > sma4[1] -> entry long when position_size <= 0
    sma9 < sma18 and sma4 < sma4[1] -> entry short when position_size > 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the short entry needs an open long, so the strategy starts long-only and then
      alternates long / short. strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths only.
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

NAME = "fmz_428089_three_sma_alternating"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length1": [18, 36],
    "length3": [4, 2],
}
DEFAULT_PARAMS = {"length1": 18, "length2": 9, "length3": 4}


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
    m1, m2, m3 = (c.rolling(int(p[k])).mean() for k in ("length1", "length2", "length3"))
    up = ((m2 > m1) & (m3 > m3.shift(1))).to_numpy()
    dn = ((m2 < m1) & (m3 < m3.shift(1))).to_numpy()
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i] and pos <= 0:
            pos = 1
        elif dn[i] and pos > 0:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
