"""EMA 8 / 21 crossings, 1-hour bars: the EMA 8 crossing the EMA 21 upward goes long, downward goes short; reversing.
Port of FMZ strategy #439830 "Momentum Moving Average Crossover Trading Strategy" (TradersPost Example MOMO Strategy).

FMZ source id: 439830

Source
    https://www.fmz.com/strategy/439830 (PineScript v5, FMZ last modified 2024-01-24 11:09:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 164-248), EMA 8 / 21; sides Both; percent mode with stop / target inputs 0 (no levels); date condition true
    tradersPostBuy = cross(fast, slow) and fast >= slow;  tradersPostSell = cross and fast <= slow;  entry Long / entry Short (sides Both);  exits with profit / loss na (inputs 0)

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the stop and target inputs at 0 the exit levels are na and no exit is placed; the
      timeConditionEnd close never fires (the condition is always true). The 30-minute EMA lines read
      with lookahead_on are only plotted and feed no order. A cross with the two EMAs equal meets both
      tests and the later short entry wins (as #437773). strategy.entry reverses: REVERSAL INTENDED. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the lookahead lines unused.
    2 generic: PASS, EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the stop / target inputs stored (0).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG439830 (2 members, best partner #440854, Jaccard 0.955); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439830_tradersposts_ema8_21_cross"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 12],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 8, "slow": 21}


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
    cr = ((f > s) & (f.shift(1) <= s.shift(1))) | ((f < s) & (f.shift(1) >= s.shift(1)))
    sell = cr & (f <= s)
    buy = cr & (f >= s) & ~sell
    false = pd.Series(False, index=c.index)
    return buy, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
