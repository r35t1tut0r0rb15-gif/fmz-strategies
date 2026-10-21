"""SMA 5 crossing over the SMA 200, 1-minute bars, long only: the cross up buys; the cross down closes an id that never trades ("Sell"), so the first long is held.
Port of FMZ strategy #438450 "基于SMA均线交叉的量化交易策略SMA-Crossover-Based-Quantitative-Trading-Strategy" (SMA Crossover Strategy).

FMZ source id: 438450

Source
    https://www.fmz.com/strategy/438450 (PineScript v4, FMZ last modified 2024-01-12 10:51:33).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 114-138), SMA 5 / 10 / 20 / 50 / 130 / 200 (only 5 and 200 trade)
    crossover(sma 5, sma 200) -> entry Buy;  crossunder(sma 5, sma 200) -> close("Sell")

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.close("Sell") names an entry id that is never used, so it closes nothing: the first long
      is held to the end of the data, as written (owed: probably close("Buy")). The other averages only
      plot. Long only. No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crossings.
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

NAME = "fmz_438450_sma5_200_cross_long_held"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 10],
    "slow": [200, 130],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 200}


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
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return up, false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
