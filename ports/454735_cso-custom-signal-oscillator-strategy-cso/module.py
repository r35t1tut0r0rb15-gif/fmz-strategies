"""The open-minus-close oscillator crossing zero, 2-hour bars: the oscillator crossing over zero (a red bar after a green one) goes long, crossing under zero (a green bar after a red one) goes short; reversing.
Port of FMZ strategy #454735 "CSO Custom Signal Oscillator Strategy CSO" (Custom Signal Oscillator Strategy (CSO-TEST)).

FMZ source id: 454735

Source
    https://www.fmz.com/strategy/454735 (PineScript v5, FMZ last modified 2024-06-21 14:26:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 214-261), fast signal open, slow signal close; long-only off
    crossover(open - close, 0) -> entry Long;  crossunder(open - close, 0) -> entry Short (long-only off)

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the default inputs the oscillator is open - close, so it crosses over zero when a bar
      closes under its open after one that did not, as written. The long-only exit is off by default,
      so positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "2h" from the
      backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle-colour flips.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_454735_open_close_oscillator_zero_cross_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    osc = bars_df["open"] - bars_df["close"]
    o1 = osc.shift(1)
    le = (osc > 0) & (o1 <= 0)
    se = (osc < 0) & (o1 >= 0)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
