"""Bollinger 20 / 2 band re-entries, 1-hour bars: the close crossing back over the lower band goes long, back under the upper band goes short; reversing.
Port of FMZ strategy #453647 "Bollinger Bands and Moving Average Crossover Strategy" (Bollinger Bands Strategy (BB Strategy)).

FMZ source id: 453647

Source
    https://www.fmz.com/strategy/453647 (PineScript v5, FMZ last modified 2024-06-07 14:52:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-127), Bollinger SMA 20 / 2
    crossover(close, lower) -> entry Buy;  crossunder(close, upper) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The basis type defaults to SMA. There is no exit: positions end at the opposite entry. REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band re-entries.
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

NAME = "fmz_453647_bollinger20_band_reentry_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 2.5],
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
    upper, lower = basis + dev, basis - dev
    c1 = c.shift(1)
    le = (c > lower) & (c1 <= lower.shift(1))
    se = (c < upper) & (c1 >= upper.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
