"""Chande momentum extremes against their own history, 1-hour bars: a CMO 9 under the 1st percentile of its last 425 values
goes long, over the 99th percentile goes short; there are no other exits (the closes are commented out).
Port of FMZ strategy #431960 "Extreme Distribution Swing Strategy" (Chande Minute Swinger).

FMZ source id: 431960

Source
    https://www.fmz.com/strategy/431960 (PineScript v4, FMZ last modified 2023-11-13 17:03:08).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 151-201), CMO 9, look-back 425, percentiles 1 / 99
    cmo = 100 (sum(up, 9) - sum(down, 9)) / (sum(up, 9) + sum(down, 9))
    buy = percentile_nearest_rank(cmo, 425, 1);  sell = percentile_nearest_rank(cmo, 425, 99)
    cmo < buy -> entry long;  cmo > sell -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * percentile_nearest_rank over the last 425 values including the current one: the value at rank
      ceil(p / 100 x n) of the sorted window, as Pine defines it. The exit percentiles only feed
      commented-out closes.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, rolling percentiles of a momentum oscillator.
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

NAME = "fmz_431960_cmo_percentile_extremes"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [9, 20],
    "pct": [1, 5],
}
DEFAULT_PARAMS = {"length": 9, "pct": 1, "lookback": 425}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _nearest_rank(x, n, pct):
    k = max(1, int(np.ceil(pct / 100 * n)))
    return x.rolling(n).apply(lambda a: np.sort(a)[k - 1], raw=True)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    mom = c.diff()
    n = int(p["length"])
    s1, s2 = mom.clip(lower=0).rolling(n).sum(), (-mom).clip(lower=0).rolling(n).sum()
    cmo = 100 * (s1 - s2) / (s1 + s2)
    lb = int(p["lookback"])
    lo_ = _nearest_rank(cmo, lb, float(p["pct"]))
    hi_ = _nearest_rank(cmo, lb, 100 - float(p["pct"]))
    lg = (cmo < lo_).astype(bool)
    sh = (cmo > hi_).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return lg & ~sh, false, sh, false.copy()


def portfolio_kwargs(**params):
    return {}
