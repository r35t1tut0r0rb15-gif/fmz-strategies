"""Smoothed CCI sign, 1-hour bars: the EMA 12 of CCI 20 above zero holds a long, below zero holds a short.
Port of FMZ strategy #430858 "基于CCI和EMA的趋势跟随交易策略CCI-and-EMA-Trend-Following-Trading-Strategy" (CCI with EMA Strategy).

FMZ source id: 430858

Source
    https://www.fmz.com/strategy/430858 (PineScript v4, FMZ last modified 2023-11-02 15:17:22).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 146-175), CCI 20, EMA 12, buy / sell points 0
    cciema = ema(cci(close, 20), 12); cciema > 0 -> entry long;  cciema < 0 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The commented-out exits are not used. strategy.entry reverses: REVERSAL INTENDED.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, the sign of a smoothed CCI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity per entry stored in original_sizing.txt.
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

NAME = "fmz_430858_cci_ema_sign"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "length_cci_ema": [12, 24],
}
DEFAULT_PARAMS = {"length": 20, "length_cci_ema": 12, "buy_point": 0.0, "sell_point": 0.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _cci(src, n):
    ma = src.rolling(n).mean()
    dev = src.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    return (src - ma) / (0.015 * dev.replace(0.0, np.nan))


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
    ce = _cci(bars_df["close"], int(p["length"])).ewm(span=int(p["length_cci_ema"]), adjust=False).mean().to_numpy()
    m = len(ce)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if ce[i] > p["buy_point"]:
            pos = 1
        elif ce[i] < p["sell_point"]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
