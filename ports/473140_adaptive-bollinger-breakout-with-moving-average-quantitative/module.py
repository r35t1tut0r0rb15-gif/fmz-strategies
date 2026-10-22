"""Bollinger 20 / 2 band breakouts, 1-hour bars: a close crossing over the upper band goes long, a close crossing under the lower band goes short; reversing.
Port of FMZ strategy #473140 "Adaptive Bollinger Breakout with Moving Average Quantitative Strategy System" (BB Breakout with MA 100 Strategy).

FMZ source id: 473140

Source
    https://www.fmz.com/strategy/473140 (PineScript v5, FMZ last modified 2024-11-27 15:55:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 104-151), BB 20, 2 sd; SMA 100 plotted only; qty = equity / close
    close > upper and close[1] <= upper[1] -> entry Long;  close < lower and close[1] >= lower[1] -> entry Short;  closes on the opposite signal

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes come with the reversing entries (#437773). The equity-based quantity is not ported.
      REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: equity-based quantity stored, not ported.
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

NAME = "fmz_473140_bb20_band_breakout_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "std_dev": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "std_dev": 2.0}


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
    dev = float(p["std_dev"]) * c.rolling(n).std(ddof=0)
    up, lo = basis + dev, basis - dev
    le = (c > up) & (c.shift(1) <= up.shift(1))
    se = (c < lo) & (c.shift(1) >= lo.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
