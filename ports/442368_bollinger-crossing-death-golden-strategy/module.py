"""Bollinger (50, 2.5) breakouts, 1-hour bars: the close crossing over the upper band goes long, crossing under the lower band goes short; reversing.
Port of FMZ strategy #442368 "Bollinger Crossing Death Golden Strategy" (Optimized Bollinger Bands Strategy for Gold).

FMZ source id: 442368

Source
    https://www.fmz.com/strategy/442368 (PineScript v4, FMZ last modified 2024-02-21 14:19:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 135-167), BB 50 x 2.5
    crossover(close, upper) -> entry Buy;  crossunder(close, lower) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's stdev is the population deviation. strategy.entry reverses: REVERSAL INTENDED. No sizing
      code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band breakouts.
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

NAME = "fmz_442368_bb50_breakout_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 20],
    "mult": [2.5, 2.0],
}
DEFAULT_PARAMS = {"length": 50, "mult": 2.5}


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
    up, dn = basis + dev, basis - dev
    le = (c > up) & (c.shift(1) <= up.shift(1))
    se = (c < dn) & (c.shift(1) >= dn.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
