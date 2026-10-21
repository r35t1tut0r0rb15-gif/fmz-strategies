"""Bollinger band breakouts, 1-hour bars, long only: the close crossing over the upper band (SMA 20 + 1.5 sigma) buys; crossing under the lower band closes the long (exit option 1).
Port of FMZ strategy #437565 "Bollinger Band Breakout Strategy" (BB-BO).

FMZ source id: 437565

Source
    https://www.fmz.com/strategy/437565 (PineScript v4, FMZ last modified 2024-01-03 17:53:32).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 151-171), period 20, 1.5 sigma, exit option 1 (lower band)
    crossover(close, upper) -> entry Long (qty 1);  exit 1: crossunder(close, lower) -> close Long;  exit 2: crossunder(close, basis)

Interpretation choices (Pine rules in SURVEY_README.md)
    * stdev is the population deviation. Exit option 2 (the middle band) is an alternative input and is
      swept in the grid. Long only. The fixed quantity 1 is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG437565 (2 members, best partner #440308, Jaccard 0.895); ND426339 (2 members, best partner #426339, Jaccard 0.661); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437565_bb_breakout_band_exit_long"
FAMILY = "bollinger_breakout"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [1.5, 2.0],
    "exit_option": [1, 2],
}
DEFAULT_PARAMS = {"length": 20, "mult": 1.5, "exit_option": 1}


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
    up, lo = basis + dev, basis - dev
    ent = (c > up) & (c.shift(1) <= up.shift(1))
    ref = lo if int(p["exit_option"]) == 1 else basis
    ex = (c < ref) & (c.shift(1) >= ref.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return ent, ex, false, false.copy()


def portfolio_kwargs(**params):
    return {}
