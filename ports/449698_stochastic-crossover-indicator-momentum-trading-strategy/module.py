"""Stochastic (14, 3, 3) crossings at the extremes, 1-hour bars: %K crossing over %D under 20 goes long, crossing under %D over 80 goes short; reversing.
Port of FMZ strategy #449698 "Stochastic Crossover Indicator Momentum Trading Strategy" (Stochastic Crossover (Stochastic Crossover Buy/Sell)).

FMZ source id: 449698

Source
    https://www.fmz.com/strategy/449698 (PineScript v4, FMZ last modified 2024-04-28 11:57:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-123), stochastic 14, K 3, D 3; levels 20 / 80
    crossover(k, d) and k < 20 -> entry Buy, close Sell;  crossunder(k, d) and k > 80 -> close Buy, entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each close comes with the opposite entry on the same bar: one reversal. REVERSAL INTENDED. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic crossings at the extremes.
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

NAME = "fmz_449698_stoch_cross_at_extremes_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "smooth": [3, 5],
}
DEFAULT_PARAMS = {"length": 14, "smooth": 3, "os": 20.0, "ob": 80.0}


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
    n, s = int(p["length"]), int(p["smooth"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).where(hh > ll)).rolling(s).mean()
    d = k.rolling(s).mean()
    le = (k > d) & (k.shift(1) <= d.shift(1)) & (k < float(p["os"]))
    se = (k < d) & (k.shift(1) >= d.shift(1)) & (k > float(p["ob"]))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
