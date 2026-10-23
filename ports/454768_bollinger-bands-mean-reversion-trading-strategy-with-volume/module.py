"""Hourly bars: the close crossing back over the lower Bollinger band (20, 2) goes long, crossing under the upper band goes short; each signal also closes the other side; reversing.
Port of FMZ strategy #454768 "Bollinger Bands Mean Reversion Trading Strategy with Volume Filter" (Mean Regression Strategy).

FMZ source id: 454768

Source
    https://www.fmz.com/strategy/454768 (PineScript v5, FMZ last modified 2024-06-21 18:20:13).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 174-221), BB 20 x 2; volume filter on with threshold 100000 (no effect)
    longCondition = crossover(close, lower) -> entry Long, close Short;  shortCondition = crossunder(close, upper) -> entry Short, close Long
    if useVolumeFilter: the same calls again with the conditions and volume > 100000

Interpretation choices (Pine rules in SURVEY_README.md)
    * The orders are first sent with the unfiltered conditions, so the second, volume-filtered copy
      (volume > 100000, an absolute threshold) can only repeat orders already sent: it changes nothing
      (weird case; held for volume, not used). The closes fire with the opposite entry and act only on a
      position the entry leaves unchanged. Pine's stdev is the population deviation. REVERSAL INTENDED. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger band re-entries.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_454768_bollinger_reentry_reversal_1h"
FAMILY = "bollinger_reversion"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    up = (c > lower) & (c.shift(1) <= lower.shift(1))
    dn = (c < upper) & (c.shift(1) >= upper.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (up & ~dn).astype(bool), false, dn.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
