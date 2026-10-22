"""Bollinger 20 / 2 crossings, 2-hour bars: the close crossing over the lower band or the basis goes long; crossing under the upper band or the basis goes short; reversing.
Port of FMZ strategy #451700 "Bollinger-Bands-布林带策略精准交易实现最大收益-Bollinger-Bands-Strategy-Precision-Trading-for-Maximum-Gains" (Bollinger Bands Strategy with Long and Short).

FMZ source id: 451700

Source
    https://www.fmz.com/strategy/451700 (PineScript v5, FMZ last modified 2024-05-17 10:32:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-161), Bollinger 20 / 2
    crossover(close, lower) or crossover(close, basis) -> entry Long;  crossunder(close, upper) or crossunder(close, basis) -> close Long
    crossunder(close, upper) or crossunder(close, basis) -> entry Short;  crossover(close, lower) or crossover(close, basis) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short entry is the long close and the short close is the long entry, so every signal
      reverses: on a buy bar the entry reverses the short and the close then finds it reversed; on a
      sell bar the long is closed and the short opened (one reversal). The buy and sell crossings
      cannot meet on one bar. REVERSAL INTENDED. No sizing code. FREQ = "2h" from the backtest header
      (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band and basis crossings.
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

NAME = "fmz_451700_bollinger_lower_basis_cross_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
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

    def over(x):
        return (c > x) & (c1 <= x.shift(1))

    def under(x):
        return (c < x) & (c1 >= x.shift(1))

    buy = over(lower) | over(basis)
    sell = under(upper) | under(basis)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
