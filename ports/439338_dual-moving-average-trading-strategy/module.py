"""EMA 5 / 15 crossings, bar size from the driver: the EMA 5 crossing over the EMA 15 goes long, crossing under goes short; reversing.
Port of FMZ strategy #439338 "Dual Moving Average Trading Strategy" (CS: 2 Moving Averages Script - Strategy (Testing)).

FMZ source id: 439338

Source
    https://www.fmz.com/strategy/439338 (PineScript v3, FMZ last modified 2024-01-19 14:10:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 140-179), MA 1 EMA 5 of close; MA 2 EMA 15 of close; window() always true
    enterLong = crossover(ma1, ma2);  exitLong = crossover(ma2, ma1);  entry Long Entry when enterLong;  entry Short Entry when exitLong

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no backtest header and names no chart period: FREQ = "bar_size_pending" (rule 1),
      bars from the house bar_sizes.build_bars with the driver's bar_size. window() returns true.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings.
    3 crypto-exchange-only: no (no exchange named).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_439338_ema5_15_cross_bar_size_pending"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1_length": [5, 10],
    "ma2_length": [15, 30],
}
DEFAULT_PARAMS = {"ma1_length": 5, "ma2_length": 15}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a = c.ewm(span=int(p["ma1_length"]), adjust=False).mean()
    b = c.ewm(span=int(p["ma2_length"]), adjust=False).mean()
    up = (a > b) & (a.shift(1) <= b.shift(1))
    dn = (b > a) & (b.shift(1) <= a.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
