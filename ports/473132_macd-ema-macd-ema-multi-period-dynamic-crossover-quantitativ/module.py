"""MACD 12 / 26 / 9 crossings, 1-hour bars, long only: the MACD crossing over its signal buys; crossing under sells. Same rules as #471715 at its default setting (near-duplicate group, rule 7).
Port of FMZ strategy #473132 "MACD-EMA多周期动态交叉量化交易系统-MACD-EMA-Multi-Period-Dynamic-Crossover-Quantitative-Trading-System" (REEL TIME MACD Strategy with Alerts and EMAs).

FMZ source id: 473132

Source
    https://www.fmz.com/strategy/473132 (PineScript v5, FMZ last modified 2024-11-27 14:58:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-144), MACD 12 / 26 / 9; EMA 10 / 20 / 50 / 100 / 200 plotted only
    crossover(macd, signal) -> entry Buy;  crossunder(macd, signal) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The rules are those of #471715 (C211) at its default MACD setting; the EMAs and alerts are drawing
      only. The grid is #471715's menu index. Long only. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473132_macd12_26_9_cross_long_with_emas"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "setting": [0, 1, 2],
}
DEFAULT_PARAMS = {"setting": 0}
SETTINGS = ((12, 26, 9), (5, 35, 5), (8, 17, 9))   # the settings of #471715's grid


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
    f, s, g = SETTINGS[int(p["setting"])]
    c = bars_df["close"]
    macd = c.ewm(span=f, adjust=False).mean() - c.ewm(span=s, adjust=False).mean()
    sig = macd.ewm(span=g, adjust=False).mean()
    le = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    lx = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
