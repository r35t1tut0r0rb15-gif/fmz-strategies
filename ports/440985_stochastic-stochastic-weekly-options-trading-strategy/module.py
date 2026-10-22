"""Stochastic 20 / 80 crossings, 2-hour bars: K (14) crossing over 20 goes long (closing a short), crossing under 80 goes short (closing a long); reversing.
Port of FMZ strategy #440985 "基于Stochastic指标的周期性期权交易策略Stochastic-Weekly-Options-Trading-Strategy" (WOS).

FMZ source id: 440985

Source
    https://www.fmz.com/strategy/440985 (PineScript v5, FMZ last modified 2024-02-04 15:14:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 108-126), stochastic 14, D 3 (plotted); levels 20 / 80
    longEntry = crossover(K, 20) -> entry Long;  longExit = crossunder(K, 80) -> close Long;  shortEntry = crossunder(K, 80) -> entry Short;  shortExit = crossover(K, 20) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The calls run in the written order: a cross under 80 closes the long and then enters the short; a
      cross over 20 enters the long, and the short close written after it leaves the reversal standing
      (as #438020). strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "2h" from the
      backtest header (bars on UTC multiples of 2 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic level crossings.
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

NAME = "fmz_440985_stochastic_20_80_cross_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "low_level": [20, 30],
}
DEFAULT_PARAMS = {"length": 14, "low_level": 20}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    lv = float(p["low_level"])
    hv = 100 - lv
    up = (k > lv) & (k.shift(1) <= lv)
    dn = (k < hv) & (k.shift(1) >= hv)
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
