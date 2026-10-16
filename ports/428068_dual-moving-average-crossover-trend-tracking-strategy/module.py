"""EMA 10 / 20 cross, hourly bars: EMA 10 crossing above EMA 20 goes long, crossing below goes short.
Port of FMZ strategy #428068 "Dual Moving Average Crossover Trend Tracking Strategy" (KSR Strategy).

FMZ source id: 428068

Source
    https://www.fmz.com/strategy/428068 (PineScript v4, FMZ last modified 2023-09-28 11:52:16).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 224-273), EMA 10 / 20
    crossover(ema10, ema20) -> entry long; crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Heikin Ashi daily / weekly securities, EMA 100 and EMA 16 are drawn only (no order uses
      them).
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the higher-timeframe securities reach no order.
    2 generic: PASS, EMA lengths only.
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

NAME = "fmz_428068_ema_10_20_cross"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "par1": [10, 5],
    "par2": [20, 50],
}
DEFAULT_PARAMS = {"par1": 10, "par2": 20}


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
    a = c.ewm(span=int(p["par1"]), adjust=False).mean()
    b = c.ewm(span=int(p["par2"]), adjust=False).mean()
    up = ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    dn = ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()
    m = len(up)
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
