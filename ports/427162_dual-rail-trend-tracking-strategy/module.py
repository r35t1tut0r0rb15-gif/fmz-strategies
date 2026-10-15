"""Bollinger band rebound, long only: the close crossing back above the lower band (20, 2) goes
long; the close crossing back under the upper band closes the long.
Port of FMZ strategy #427162 "Dual-Rail Trend Tracking Strategy".

FMZ source id: 427162

Source
    https://www.fmz.com/strategy/427162 (PineScript v5, FMZ last modified 2023-09-18 17:31:43).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 183-205), length 20, multiplier 2.0, source close
    crossover(close, sma - 2 stdev) -> entry long; crossunder(close, sma + 2 stdev) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.stdev is the population standard deviation. The offset input only shifts the plot.
    * Entries only from flat (pyramiding 0); one signal per bar (the two crosses cannot coincide).
    * FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a band in standard deviations.
    3 crypto-exchange-only: no (spot pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: ND427162 (with #429561, Jaccard 0.683); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427162_bb_rebound_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 14, 30],
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
    basis, dev = c.rolling(n).mean(), p["mult"] * c.rolling(n).std(ddof=0)
    lower, upper = basis - dev, basis + dev
    entry = ((c > lower) & (c.shift(1) <= lower.shift(1))).to_numpy()
    exit_ = ((c < upper) & (c.shift(1) >= upper.shift(1))).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and entry[i]:
            le[i], pos = True, 1
        elif pos == 1 and exit_[i]:
            lx[i], pos = True, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
