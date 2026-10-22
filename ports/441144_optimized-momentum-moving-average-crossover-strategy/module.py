"""SMA 10 / 20 crossings, 2-hour bars: the SMA 10 crossing over the SMA 20 goes long, crossing under goes short; reversing.
Port of FMZ strategy #441144 "Optimized Momentum Moving Average Crossover Strategy" (Improved Moving Average Crossover).

FMZ source id: 441144

Source
    https://www.fmz.com/strategy/441144 (PineScript v4, FMZ last modified 2024-02-06 10:27:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 197-236), SMA 10 / 20; risk inputs (lot size computed, unused)
    crossover -> entry Buy, close Sell;  crossunder -> close Buy, entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * lotSize is computed but never passed to an order. Each close follows the opposite entry and leaves
      the reversal standing (as #438020). strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ
      = "2h" from the backtest header (bars on UTC multiples of 2 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (lot size unused).
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

NAME = "fmz_441144_sma10_20_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 20],
    "slow": [20, 50],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 20}


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
    c = bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
