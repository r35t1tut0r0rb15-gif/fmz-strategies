"""Five-bar percentage change, 3-hour bars: a close more than 0.4 % above the close 5 bars back goes long, more than 0.4 %
below goes short.
Port of FMZ strategy #431885 "Momentum Reversal Strategy" (Percentage Change strategy w/BG color).

FMZ source id: 431885

Source
    https://www.fmz.com/strategy/431885 (PineScript v4, FMZ last modified 2023-11-13 10:02:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 199-266), x 5, +0.4 % / -0.4 %
    change = (close - close[5]) / close[5] x 100;  change > 0.4 -> entry long;  change < -0.4 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries are re-issued while the condition holds; strategy.entry reverses: REVERSAL INTENDED.
      FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a percentage change.
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

NAME = "fmz_431885_five_bar_change_momentum"
FAMILY = "momentum_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "x": [5, 10],
    "pct": [0.4, 1.0],
}
DEFAULT_PARAMS = {"x": 5, "pct": 0.4}


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
    k = int(p["x"])
    ch = (c - c.shift(k)) / c.shift(k) * 100
    lg = (ch > p["pct"]).astype(bool)
    sh = (ch < -p["pct"]).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return lg, false, sh, false.copy()


def portfolio_kwargs(**params):
    return {}
