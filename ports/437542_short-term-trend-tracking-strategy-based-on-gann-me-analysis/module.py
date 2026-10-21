"""Guppy-style EMA ribbon difference, 1-hour bars: the sum of the six slow EMAs (30 ... 60) minus the sum of the six fast EMAs (3 ... 15) crossing over zero goes long, crossing under goes short; reversing.
Port of FMZ strategy #437542 "Short term Trend Tracking Strategy Based on Gann Me Analysis Indicator" (GMAE Original (By Kevin Manrrique)).

FMZ source id: 437542

Source
    https://www.fmz.com/strategy/437542 (PineScript v2, FMZ last modified 2024-01-03 16:10:08).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 144-217), fast EMAs 3 / 5 / 8 / 10 / 12 / 15, slow EMAs 30 / 35 / 40 / 45 / 50 / 60 of the close
    gmae = (ema 30 + 35 + 40 + 45 + 50 + 60) - (ema 3 + 5 + 8 + 10 + 12 + 15);  crossover(gmae, 0) -> entry long;  crossunder(gmae, 0) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The sign of the ribbon difference is scale-free (a crossing of zero), so the price-unit sum needs no
      re-expression. As written, a long fires when the SLOW ribbon rises above the fast one. REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, sign of an EMA ribbon difference.
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

NAME = "fmz_437542_ema_ribbon_difference_cross"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "scale": [1.0, 2.0],
}
DEFAULT_PARAMS = {"scale": 1.0}
FAST = (3, 5, 8, 10, 12, 15)
SLOW = (30, 35, 40, 45, 50, 60)


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
    k = float(p["scale"])
    g = sum(c.ewm(span=max(1, int(round(n * k))), adjust=False).mean() for n in FAST)
    mae = sum(c.ewm(span=max(1, int(round(n * k))), adjust=False).mean() for n in SLOW)
    x = mae - g
    up = (x > 0) & (x.shift(1) <= 0)
    dn = (x < 0) & (x.shift(1) >= 0)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
