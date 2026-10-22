"""Bollinger band closes, 1-hour bars: a close under the lower band (SMA 20 - 2 sigma) holds a long, a close over the upper band holds a short; reversing.
Port of FMZ strategy #439201 "Bollinger Bands Breakout Strategy" (BB Strategy).

FMZ source id: 439201

Source
    https://www.fmz.com/strategy/439201 (PineScript v5, FMZ last modified 2024-01-18 12:18:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 156-170), BB 20 x 2
    close < lower -> entry Buy;  close > upper -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are states, so the entries are sent on every bar beyond a band. stdev is the population
      deviation. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger band levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG439201 (2 members, best partner #443089, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439201_bb_band_close_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0}


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
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    false = pd.Series(False, index=c.index)
    return c < basis - dev, false, c > basis + dev, false.copy()


def portfolio_kwargs(**params):
    return {}
