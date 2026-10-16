"""EMA 3 / EMA 9 cross, long only, 4-hour bars: the fast EMA crossing above the slow one goes long, crossing
below closes the long.
Port of FMZ strategy #429389 "双EMA金叉死叉策略Dual-EMA-Crossover-Strategy" (EMA Strategy).

FMZ source id: 429389

Source
    https://www.fmz.com/strategy/429389 (PineScript v4, FMZ last modified 2023-10-16 16:15:38).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 269-317), EMA 3 / 9, shorting off, stops off
    crossover(ema3, ema9) -> entry long; crossunder(ema3, ema9) -> close long
    (shorting, the 1.08 initial stop and the trailing inputs are off by default)

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Allow Shorting?", "Use Initial Stop Loss?" and "Use Trailing Stop?" default to false: long only,
      no stops (the inputs are stored). The date inputs are unused (time_cond is true).
    * Long only. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crosses only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and the off-by-default stops stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND429389 (2 members, best partner #430377, Jaccard 0.667); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429389_ema3_9_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [3, 5],
    "slow": [9, 21],
}
DEFAULT_PARAMS = {"fast": 3, "slow": 9}


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
    long_e = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    long_x = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
