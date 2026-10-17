"""SMA 7 / 25 crosses (Jacques Grobler), 1-hour bars: the SMA 7 crossing above the SMA 25 goes long, crossing below goes
short.
Port of FMZ strategy #431494 "基于SMA交叉策略SMA-Crossover-Strategy" (SimpleCrossOver_Bot_V1_Backtester).

FMZ source id: 431494

Source
    https://www.fmz.com/strategy/431494 (PineScript v4, FMZ last modified 2023-11-08 11:36:51).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 154-198), SMA 7 / 25
    crossover(sma7, sma25) -> entry long;  crossunder(sma7, sma25) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * timecondition is always true. strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the commission stored in original_sizing.txt.
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

NAME = "fmz_431494_sma_7_25_cross"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [7, 14],
    "slow": [25, 50],
}
DEFAULT_PARAMS = {"fast": 7, "slow": 25}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
