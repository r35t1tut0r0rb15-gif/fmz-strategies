"""EMA 20 / 55 crossings, 1-hour bars, long only: the cross up goes long (the "ready" latch is set and spent on the same bar), the cross down closes.
Port of FMZ strategy #449954 "Exponential Moving Average Crossover Leverage Strategy" (EMA Crossover Strategy with Leverage, Conditional Entry, and MA Option).

FMZ source id: 449954

Source
    https://www.fmz.com/strategy/449954 (PineScript v5, FMZ last modified 2024-04-30 16:26:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 123-182), EMA 20 / 55 (EMA mode); leverage 3 (sizing); dates (always true)
    crossover(ema20, ema55) -> readyToEnter;  readyToEnter -> entry Long (qty = equity x 3 / close), readyToEnter off;  crossunder -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The touch condition is commented out, so the latch fires on the crossing bar itself. The
      leveraged quantity is sizing. Long only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the leveraged quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449954_ema20_55_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "slow": [55, 100],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 55}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    lx = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
