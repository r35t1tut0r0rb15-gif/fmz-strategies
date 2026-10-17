"""Bollinger 20 / 2 and SMA 50 double crosses, 1-hour bars, long only: a close crossing above the lower band on the same bar
as it crosses above the SMA 50 goes long; a close crossing below the upper band on the same bar as it crosses below the
SMA 50 closes the long.
Port of FMZ strategy #434482 "Bollinger Bands Reversal with MA Trend Filter" (Bollinger Bands Rejection with MA Trend Filter).

FMZ source id: 434482

Source
    https://www.fmz.com/strategy/434482 (PineScript v5, FMZ last modified 2023-12-06 17:34:51).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 144-172), BB 20 / 2 on close, SMA 50 on close
    crossover(close, lower) and crossover(close, sma50) -> entry long
    crossunder(close, upper) and crossunder(close, sma50) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both crosses must happen on the same bar, as written. stdev is the population one. Long only;
      an entry while long is ignored. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band and average crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434482_bollinger_ma_double_cross_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_len": [20, 40],
    "ma_len": [50, 100],
}
DEFAULT_PARAMS = {"bb_len": 20, "mult": 2.0, "ma_len": 50}


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
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, lw = basis + dev, basis - dev
    ma = c.rolling(int(p["ma_len"])).mean()
    xo = lambda a, b: (a > b) & (a.shift(1) <= b.shift(1))  # noqa: E731
    xu = lambda a, b: (a < b) & (a.shift(1) >= b.shift(1))  # noqa: E731
    le = (xo(c, lw) & xo(c, ma)).astype(bool)
    lx = (xu(c, up) & xu(c, ma)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
