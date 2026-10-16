"""ChartArt EMA slope + cross, contrarian: the close crossing under EMA 20, or a falling close that
crosses under a falling EMA 2 while EMA 4 still rises, goes long; the mirror goes short (always in
the market after the first signal).
Port of FMZ strategy #427370 "EMA Slope and Cross Trend Trading Strategy".

FMZ source id: 427370

Source
    https://www.fmz.com/strategy/427370 (PineScript v3, FMZ last modified 2023-09-20 14:32:22).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 156-200), EMA 2 / 4 / 20
    long = crossunder(close, ema20) or (change(close) < 0 and change(ema2) < 0 and crossunder(close, ema2)
           and change(ema4) > 0)
    short = crossover(close, ema20) or (change(close) > 0 and change(ema2) > 0 and crossover(close, ema2)
            and change(ema4) < 0)

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written: a cross DOWN buys and a cross UP sells.
    * strategy.entry reverses: REVERSAL INTENDED; a bar with both conditions: the side not held
      (long first from flat).
    * FREQ = "6h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths and signs of changes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427370_chartart_ema_slope_cross_fade"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "6h"  # backtest header period: 6h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1": [2, 3],
    "ma2": [4, 8],
    "ma3": [20, 50],
}
DEFAULT_PARAMS = {"ma1": 2, "ma2": 4, "ma3": 20}


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
    m1, m2, m3 = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("ma1", "ma2", "ma3"))

    def xunder(a, b):
        return (a < b) & (a.shift(1) >= b.shift(1))

    def xover(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    dc, d1, d2 = c.diff(), m1.diff(), m2.diff()
    long_c = (xunder(c, m3) | ((dc < 0) & (d1 < 0) & xunder(c, m1) & (d2 > 0))).to_numpy()
    short_c = (xover(c, m3) | ((dc > 0) & (d1 > 0) & xover(c, m1) & (d2 < 0))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i] and pos != 1:
            pos = 1
        elif short_c[i] and pos != -1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
