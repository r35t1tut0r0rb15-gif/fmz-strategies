"""Close crossings of the SMA 15, 1-hour bars: the close crossing over the SMA goes long, crossing under goes short; reversing (the SMA 200 input is never used).
Port of FMZ strategy #445464 "Dual Moving Average Crossover Quantitative Trading Strategy" (SMA Crossover Strategy (SMA 15)).

FMZ source id: 445464

Source
    https://www.fmz.com/strategy/445464 (PineScript v5, FMZ last modified 2024-03-19 17:16:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 156-188), short SMA 15; long SMA 200 (unused)
    close[1] < sma[1] and close > sma -> entry Long;  close[1] > sma[1] and close < sma -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The crossings are strict on both bars, as written. The long SMA is never computed. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close / SMA crossings.
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

NAME = "fmz_445464_close_sma15_strict_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [15, 50],
}
DEFAULT_PARAMS = {"length": 15}


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
    s = c.rolling(int(p["length"])).mean()
    c1, s1 = c.shift(1), s.shift(1)
    le = (c1 < s1) & (c > s)
    se = (c1 > s1) & (c < s)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
