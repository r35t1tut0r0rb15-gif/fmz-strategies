"""WaveTrend (10 / 21) crossings at the outer levels, 2-hour bars: WT1 crossing over WT2 at or under -60 goes long, crossing under at or over 60 goes short; reversing.
Port of FMZ strategy #482427 "Adaptive Multi Period Trading Strategy Based on Wave Trend Momentum Breakout" (WaveTrend [LazyBear] Strategy).

FMZ source id: 482427

Source
    https://www.fmz.com/strategy/482427 (PineScript v6, FMZ last modified 2025-02-18 13:52:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 87-141), channel 10, average 21; levels 60 / 53 / -60 / -53 (outer used)
    crossover(wt1, wt2) and wt1 <= -60 -> close Short, entry Long;  crossunder(wt1, wt2) and wt1 >= 60 -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each signal closes the other side and enters, which is a reversal. REVERSAL INTENDED. No sizing
      code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, WaveTrend crossings at the outer levels.
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

NAME = "fmz_482427_wavetrend10_21_outer_level_cross_reversal"
FAMILY = "wavetrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "level": [60, 53],
    "n2": [21, 34],
}
DEFAULT_PARAMS = {"level": 60, "n2": 21, "n1": 10}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ap = (h + lo + c) / 3
    n1 = int(p["n1"])
    esa = ap.ewm(span=n1, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    ci = (ap - esa) / (0.015 * d)
    wt1 = ci.ewm(span=int(p["n2"]), adjust=False).mean()
    wt2 = wt1.rolling(4).mean()
    lv = float(p["level"])
    le = (wt1 > wt2) & (wt1.shift(1) <= wt2.shift(1)) & (wt1 <= -lv)
    se = (wt1 < wt2) & (wt1.shift(1) >= wt2.shift(1)) & (wt1 >= lv)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
