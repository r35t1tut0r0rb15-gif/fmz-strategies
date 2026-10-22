"""Stochastic Momentum Index crossings at the extremes, 1-hour bars: the SMI signal (EMA 3) crossing over the SMI's EMA 10 with the SMI under -40 goes long, crossing under with the SMI over 40 goes short;
reversing.
Port of FMZ strategy #442928 "基于-Stochastics-Momentum-Index-的趋势追踪策略Momentum-Surfer-Strategy-Based-on-Stochastics-Momentum-Index" (Stochastics Momentum Index Strategy (Stoch_MTM_Doan)).

FMZ source id: 442928

Source
    https://www.fmz.com/strategy/442928 (PineScript v5, FMZ last modified 2024-02-27 14:32:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 147-201), %K length 10, %D 3; overbought 40, oversold -40
    SMI = ema(ema(close - mid(hh, ll), 3), 3) / (ema(ema(hh - ll, 3), 3) / 2) x 100 (0 when the range average is 0);  SMIsignal = ema(SMI, 3);  emasignal = ema(SMI, 10)
    crossover(SMIsignal, emasignal) and SMI < -40 -> entry Buy;  crossunder and SMI > 40 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMI crossings at the extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG442928 (2 members, best partner #444334, Jaccard 0.824); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442928_smi_signal_ema_cross_extreme_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "a": [10, 20],
    "ob": [40, 30],
}
DEFAULT_PARAMS = {"a": 10, "ob": 40, "b": 3, "ema_len": 10}


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


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    a, b = int(p["a"]), int(p["b"])
    ll, hh = lo.rolling(a).min(), h.rolling(a).max()
    rel = _ema(_ema(c - (hh + ll) / 2, b), b)
    dif = _ema(_ema(hh - ll, b), b)
    smi = (rel / (dif / 2) * 100).where(dif != 0, 0.0)
    sig = _ema(smi, b)
    es = _ema(smi, int(p["ema_len"]))
    ob = float(p["ob"])
    le = (sig > es) & (sig.shift(1) <= es.shift(1)) & (smi < -ob)
    se = (sig < es) & (sig.shift(1) >= es.shift(1)) & (smi > ob)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
