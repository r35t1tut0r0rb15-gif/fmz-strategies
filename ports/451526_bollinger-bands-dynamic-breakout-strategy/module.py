"""Bollinger 34 / 2 band breakouts, 1-hour bars: the close crossing over the upper band goes long and under the lower band goes short; crossing back under the upper band closes the long, back over the lower band closes the short; reversing.
Port of FMZ strategy #451526 "Bollinger-Bands-Dynamic-Breakout-Strategy-动态布林带突破策略" (Bollinger Bands with Strategy (MBB)).

FMZ source id: 451526

Source
    https://www.fmz.com/strategy/451526 (PineScript v5, FMZ last modified 2024-05-15 16:25:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-117), Bollinger SMA 34, multiplier 2.0
    crossover(close, upper) -> entry Long;  crossunder(close, lower) -> entry Short;  crossunder(close, upper) -> close Long;  crossover(close, lower) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are called before the closes: on a bar that jumps across both bands the entry
      reverses the held trade and the close then finds it already reversed and does nothing (the
      port drops that close). REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band breakouts with a re-entry exit.
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

NAME = "fmz_451526_bollinger34_breakout_band_reentry_exit_reversal"
FAMILY = "bollinger"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [34, 20],
    "mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 34, "mult": 2.0}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = c.rolling(n).std(ddof=0)
    upper, lower = basis + float(p["mult"]) * dev, basis - float(p["mult"]) * dev
    c1 = c.shift(1)
    le = (c > upper) & (c1 <= upper.shift(1))
    se = (c < lower) & (c1 >= lower.shift(1))
    lx = (c < upper) & (c1 >= upper.shift(1)) & ~se
    sx = (c > lower) & (c1 <= lower.shift(1)) & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
