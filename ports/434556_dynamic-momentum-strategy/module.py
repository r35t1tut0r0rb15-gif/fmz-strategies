"""SMA 14 / 28 crosses, 1-hour bars: a cross up goes long, a cross down goes short (reversing).
Port of FMZ strategy #434556 "Dynamic Momentum Strategy" (Tu Estrategia).

FMZ source id: 434556

Source
    https://www.fmz.com/strategy/434556 (PineScript v5, FMZ last modified 2023-12-07 15:26:38).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 120-142), SMA 14 / 28; EMA 30, 10 x open / close and SMA 10 plotted only
    crossover(sma14, sma28) -> entry long;  crossunder(sma14, sma28) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The plotted EMA, ratio and SMA 10 are drawing only. strategy.entry reverses: REVERSAL
      INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crosses.
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

NAME = "fmz_434556_sma_14_28_cross"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [14, 7],
    "slow": [28, 56],
}
DEFAULT_PARAMS = {"fast": 14, "slow": 28}


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
    le = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    se = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
