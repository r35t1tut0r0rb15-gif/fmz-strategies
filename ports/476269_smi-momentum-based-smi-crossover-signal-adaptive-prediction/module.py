"""Stochastic Momentum Index (14, double EMA 3) crossings of its EMA 3 signal, 45-minute bars: the cross up goes long, the cross down goes short; reversing.
Port of FMZ strategy #476269 "基于动量指标的SMI交叉信号自适应预测策略-Momentum-Based-SMI-Crossover-Signal-Adaptive-Prediction-Strategy" (SMI Strategy with Signals).

FMZ source id: 476269

Source
    https://www.fmz.com/strategy/476269 (PineScript v6, FMZ last modified 2024-12-27 15:38:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 77-141), %K 14, %D 3 (double EMA), signal EMA 3; levels 40 / -40 plotted only
    rr = close - (highest(14) + lowest(14)) / 2;  smi = 200 ema(ema(rr, 3), 3) / ema(ema(highest - lowest, 3), 3);  sig = ema(smi, 3);  crossover(smi, sig) -> entry Compra;  crossunder -> entry Venta

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.highest(14) / ta.lowest(14) with one argument read the high and the low. The 40 / -40 lines are
      plotted only. REVERSAL INTENDED. No sizing code. FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMI signal crossings.
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

NAME = "fmz_476269_smi14_signal_cross_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_k": [14, 21],
    "length_d": [3, 5],
}
DEFAULT_PARAMS = {"length_k": 14, "length_d": 3, "length_ema": 3}


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


def _ema2(x, n):
    return x.ewm(span=n, adjust=False).mean().ewm(span=n, adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length_k"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    d = int(p["length_d"])
    first = hh.first_valid_index()
    rr = (c - (hh + ll) / 2).loc[first:]
    hl = (hh - ll).loc[first:]
    smi = (200 * (_ema2(rr, d) / _ema2(hl, d))).reindex(c.index)
    sig = smi.ewm(span=int(p["length_ema"]), adjust=False).mean()
    le = (smi > sig) & (smi.shift(1) <= sig.shift(1))
    se = (smi < sig) & (smi.shift(1) >= sig.shift(1))
    return le, pd.Series(False, index=c.index), se, pd.Series(False, index=c.index)


def portfolio_kwargs(**params):
    return {}
