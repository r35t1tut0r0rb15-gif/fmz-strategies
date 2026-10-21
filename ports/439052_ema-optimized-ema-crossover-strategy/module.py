"""EMA 7 / 20 crossings, 45-minute bars: the cross up goes long, the cross down goes short; reversing (the opposite-side closes on the same crossings act on trades the reversal already closed).
Port of FMZ strategy #439052 "优化EMA黄金交叉策略Optimized-EMA-Crossover-Strategy" (EMA15).

FMZ source id: 439052

Source
    https://www.fmz.com/strategy/439052 (PineScript v4, FMZ last modified 2024-01-17 12:01:59).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 183-213), EMA 7 / 20; risk-reward 2.5 (sizing only)
    crossover(fast, slow) -> entry Long, close Short;  crossunder -> entry Short, close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes fire on the same crossings as the opposite entries and act on trades the reversing entry
      already closed, so the reversal stands (as #438020). The ATR-based position size is sizing.
      strategy.entry reverses: REVERSAL INTENDED. FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the ATR-based size stored.
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

NAME = "fmz_439052_ema7_20_cross_45m"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [7, 12],
    "slow": [20, 50],
}
DEFAULT_PARAMS = {"fast": 7, "slow": 20}


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
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
