"""Oversold MACD crossings, no bar size of its own, long only: the MACD (EMA 12 / 26) crossing over its EMA 9 signal while the MACD is
below a small negative level goes long; the signal turning positive (the MACD crossing over the histogram) closes the long.
Port of FMZ strategy #435884 "运用MACD量化交易策略MACD-Quantitative-Trading-Strategy" (MACD - EURUSD).

FMZ source id: 435884

Source
    https://www.fmz.com/strategy/435884 (PineScript v3, FMZ last modified 2023-12-19 15:11:57).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 95-126), MACD 12 / 26 / 9 with EMAs; entry level -0.00025 (a forex price unit)
    longCond = crossover(macd, signal) and macd < -0.00025;  exitLong = crossover(macd, hist);  longCond -> entry long;  exitLong -> close long   (hist = macd - signal)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the -0.00025 level is a price unit of EURUSD (about 0.00023 of a price near 1.1);
      the port uses a fraction of the close, macd < -level_frac x close, with 0.00023 as the reading and
      0.001 as a wider level. crossover(macd, hist) is true when macd rises over macd - signal, i.e.
      when the signal line turns from non-positive to positive, as written. The source has no backtest
      header and names no bar size: FREQ = "bar_size_pending" (rule 1); precompute builds the bars with the
      house bar_sizes.build_bars(raw_1m_df, params["bar_size"]); the driver supplies bar_size. Long only.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit level -> fraction of the close.
    3 crypto-exchange-only: no.
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_435884_oversold_macd_cross_long"
FAMILY = "macd_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "bar_size_pending"
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "level_frac": [0.00023, 0.001],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "level_frac": 0.00023}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    hist = macd - sig
    le = ((macd > sig) & (macd.shift(1) <= sig.shift(1)) & (macd < -float(p["level_frac"]) * c)).fillna(False).astype(bool)
    lx = ((macd > hist) & (macd.shift(1) <= hist.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
