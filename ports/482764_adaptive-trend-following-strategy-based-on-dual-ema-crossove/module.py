"""EMA 10 / 20 crosses confirmed by the close beyond both EMAs, always in, hourly bars.
Port of FMZ strategy #482764 "基于双均线交叉的趋势跟踪自适应策略-Adaptive-Trend-Following-Strategy-Based-on-Dual-EMA-Crossover-System" (BFX Buy and Sell).

FMZ source id: 482764

Source
    https://www.fmz.com/strategy/482764 (PineScript v5, FMZ last modified 2025-02-27 17:52:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 99-127), EMA 10 / 20
    crossover(ema10, ema20) and close > both -> entry long; crossunder and close < both -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries reverse (REVERSAL INTENDED); always in after the first signal. Signal module, no stops.
      FREQ = "1h" from the backtest header. #482687 is the same script with a date window.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, two EMAs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
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

NAME = "fmz_482764_ema10_20_cross_confirmed_always_in"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 5],
    "slow": [20, 50],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 20}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (c > f) & (c > s)).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & (c < f) & (c < s)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
