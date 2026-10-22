"""WaveTrend (10, 21) line crossings, 1-hour bars: WT1 crossing over its 4-bar average goes long, crossing under goes short; reversing (the overbought / oversold levels only plot).
Port of FMZ strategy #449714 "基于WaveTrend指标的趋势追踪策略WaveTrend-Cross-LazyBear-Strategy" (WT_CROSS_LB (WaveTrend with Crosses [LazyBear])).

FMZ source id: 449714

Source
    https://www.fmz.com/strategy/449714 (PineScript v5, FMZ last modified 2024-04-28 13:56:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 127-179), channel 10, average 21; levels 60 / 53 / -60 / -53 (plot only)
    crossover(wt1, wt2) -> (position <= 0: close Sell), entry Buy;  crossunder(wt1, wt2) -> (position >= 0: close Buy), entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each crossing first closes the opposite position (the guard position <= 0 / >= 0 includes it)
      and then enters: together they are one reversal. REVERSAL INTENDED. No sizing code. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, WaveTrend line crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_449714_wavetrend_10_21_cross_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n1": [10, 9],
    "n2": [21, 12],
}
DEFAULT_PARAMS = {"n1": 10, "n2": 21}


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
    ap = (bars_df["high"] + bars_df["low"] + bars_df["close"]) / 3
    n1, n2 = int(p["n1"]), int(p["n2"])
    esa = ap.ewm(span=n1, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    ci = (ap - esa) / (0.015 * d)
    wt1 = ci.ewm(span=n2, adjust=False).mean()
    wt2 = wt1.rolling(4).mean()
    le = (wt1 > wt2) & (wt1.shift(1) <= wt2.shift(1))
    se = (wt1 < wt2) & (wt1.shift(1) >= wt2.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
