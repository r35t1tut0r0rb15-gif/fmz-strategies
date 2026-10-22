"""MACD 12 / 26 / 9 crossings, 1-hour bars, long only: the MACD crossing over its signal buys; crossing under sells.
Port of FMZ strategy #471715 "MACD动态趋势量化交易策略进阶版-Advanced-MACD-Dynamic-Trend-Quantitative-Trading-Strategy" (Hanzo - Top 10 MACD Strategy).

FMZ source id: 471715

Source
    https://www.fmz.com/strategy/471715 (PineScript v5, FMZ last modified 2024-11-12 16:27:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-185), MACD setting menu (default "Standard (12, 26, 9)")
    crossover(macd, signal) -> entry Buy;  crossunder(macd, signal) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the default menu setting is the source's rule; the grid tries other entries of the source's
      own menu. Long only. No sizing code. FREQ = "1h" from the backtest header.

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

NAME = "fmz_471715_macd_menu_cross_long"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "setting": [0, 1, 2],
}
DEFAULT_PARAMS = {"setting": 0}
SETTINGS = ((12, 26, 9), (5, 35, 5), (8, 17, 9))   # three entries of the source's menu


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
