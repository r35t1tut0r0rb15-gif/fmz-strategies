"""Two simultaneous EMA crosses, 1-hour bars: the EMA 9 and the EMA 21 crossing over the EMA 50 and the EMA 200 on the same bar goes
long; both crossing under on the same bar goes short (reversing).
Port of FMZ strategy #435485 "Four EMA Crossover Strategy" (Four EMA Crossover).

FMZ source id: 435485

Source
    https://www.fmz.com/strategy/435485 (PineScript v4, FMZ last modified 2023-12-15 11:55:36).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 158-180), EMA 9 / 21 against EMA 50 / 200
    longCondition = crossover(ema9, ema50) and crossover(ema21, ema200);  shortCondition = crossunder(ema9, ema50) and crossunder(ema21, ema200)
    longCondition -> entry long;  shortCondition -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both crosses must happen on the same bar, as written (a rare event). strategy.entry reverses:
      REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crosses.
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

NAME = "fmz_435485_four_ema_same_bar_cross"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast1": [9, 5],
    "slow2": [200, 100],
}
DEFAULT_PARAMS = {"fast1": 9, "fast2": 21, "slow1": 50, "slow2": 200}


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
    f1, f2, s1, s2 = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("fast1", "fast2", "slow1", "slow2"))
    up = ((f1 > s1) & (f1.shift(1) <= s1.shift(1))) & ((f2 > s2) & (f2.shift(1) <= s2.shift(1)))
    dn = ((f1 < s1) & (f1.shift(1) >= s1.shift(1))) & ((f2 < s2) & (f2.shift(1) >= s2.shift(1)))
    false = pd.Series(False, index=bars_df.index)
    return up.fillna(False).astype(bool), false, dn.fillna(False).astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
