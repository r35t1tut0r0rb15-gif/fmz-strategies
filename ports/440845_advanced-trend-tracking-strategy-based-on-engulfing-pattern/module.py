"""Fractal entries, 1-hour bars: a confirmed swing high (pivot high 2 / 2) goes long, a confirmed swing low goes short; reversing (the engulfing / EMA / zone signals are only plotted).
Port of FMZ strategy #440845 "Advanced Trend Tracking Strategy Based on Engulfing Pattern and Quantitative Indicators" (Engulfing Candles with Fractals, Moving Average, Demand & Supply).

FMZ source id: 440845

Source
    https://www.fmz.com/strategy/440845 (PineScript v5, FMZ last modified 2024-02-02 16:48:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 152-201), EMA 14; demand / supply 20; fractals pivothigh / pivotlow (2, 2)
    fractalUp = pivothigh(high, 2, 2) -> entry Buy;  fractalDown = pivotlow(low, 2, 2) -> entry Sell;  (buySignal / sellSignal from engulfing, EMA and zones feed plots only)

Interpretation choices (Pine rules in SURVEY_README.md)
    * A pivot is confirmed two bars after its centre, so the signal uses past bars only. As written a
      swing high buys and a swing low sells. The short entry is written after the long one and wins on a
      bar with both (as #437773). strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; pivots confirmed from past bars.
    2 generic: PASS, swing pivots.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440845_confirmed_fractal_entries"
FAMILY = "pivot_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bars": [2, 3],
}
DEFAULT_PARAMS = {"bars": 2}


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


def _pivot(x, left, right, high):
    """Pine pivothigh / pivotlow: True on the bar that confirms the centre `right` bars back (strict)."""
    c = x.shift(right)
    ok = c.notna()
    for k in range(1, left + 1):
        ok &= (c > x.shift(right + k)) if high else (c < x.shift(right + k))
    for k in range(right):
        ok &= (c > x.shift(k)) if high else (c < x.shift(k))
    return ok.fillna(False)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["bars"])
    up = _pivot(bars_df["high"], n, n, True)
    dn = _pivot(bars_df["low"], n, n, False)
    false = pd.Series(False, index=bars_df.index)
    return up & ~dn, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
