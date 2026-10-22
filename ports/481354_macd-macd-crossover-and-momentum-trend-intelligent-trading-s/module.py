"""MACD (12 / 26 / 9) signal crossings, 2-hour bars, long only: the cross up buys, the cross down closes.
Port of FMZ strategy #481354 "MACD交叉策略与动量趋势智能交易系统-MACD-Crossover-and-Momentum-Trend-Intelligent-Trading-System" (ETH/USD MACD Crossover).

FMZ source id: 481354

Source
    https://www.fmz.com/strategy/481354 (PineScript v6, FMZ last modified 2025-02-10 14:44:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-136), MACD 12 / 26 / 9
    crossover(macd, signal) -> entry Buy;  crossunder -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only. No sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD signal crossings.
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

NAME = "fmz_481354_macd_signal_cross_long"
FAMILY = "macd"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 21],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    le = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    lx = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
