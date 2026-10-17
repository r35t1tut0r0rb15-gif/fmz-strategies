"""SMA 10 / 20 crosses, 1-hour bars, long only: the SMA 10 crossing above the SMA 20 goes long, crossing below closes it.
Port of FMZ strategy #433923 "Dual Moving Average Crossover Strategy" (Moving Average Crossover Strategy).

FMZ source id: 433923

Source
    https://www.fmz.com/strategy/433923 (PineScript v4, FMZ last modified 2023-12-01 14:53:05).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 117-134), SMA 10 / 20
    crossover(sma10, sma20) -> entry long;  crossunder(sma10, sma20) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only; Opposite entries cannot occur. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433923_sma_10_20_long"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short": [10, 20],
    "long": [20, 50],
}
DEFAULT_PARAMS = {"short": 10, "long": 20}


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
    a = c.rolling(int(p["short"])).mean()
    b = c.rolling(int(p["long"])).mean()
    le = ((a > b) & (a.shift(1) <= b.shift(1))).astype(bool)
    lx = ((a < b) & (a.shift(1) >= b.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
