"""Coinrule's multi moving-average crossing, 1-hour bars, long only: the SMA 50 crossing over the SMA 100 buys; the SMA 9 crossing under the SMA 50 closes.
Port of FMZ strategy #438470 "Multi level Moving Average Crossing Strategy for Quant Masters" (Multi Moving Average Crossing).

FMZ source id: 438470

Source
    https://www.fmz.com/strategy/438470 (PineScript v4, FMZ last modified 2024-01-12 12:11:02).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 127-158), SMA 100 / 50 / 9; 30 % of equity, capital 1000, commission 0.1 %; date window true
    crossover(sma 50, sma 100) -> entry long;  crossunder(sma 9, sma 50) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * window() is true. Long only. The size, capital and commission are sizing / costs. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND429460 (2 members, best partner #429460, Jaccard 0.662); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438470_sma50_100_entry_sma9_50_exit_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "inlong": [100, 200],
    "inshort": [9, 20],
}
DEFAULT_PARAMS = {"inlong": 100, "inshort": 9, "inmid": 50}


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
    ml = c.rolling(int(p["inlong"])).mean()
    mm = c.rolling(int(p["inmid"])).mean()
    ms = c.rolling(int(p["inshort"])).mean()
    le = (mm > ml) & (mm.shift(1) <= ml.shift(1))
    lx = (ms < mm) & (ms.shift(1) >= mm.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx & ~le, false, false.copy()


def portfolio_kwargs(**params):
    return {}
