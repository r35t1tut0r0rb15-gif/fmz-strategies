"""EMA 13 / 30 crossings on the side of the EMA 100, 1-hour bars: the cross up with both EMAs over the EMA 100 goes long, the cross down with both under it goes short; reversing.
Port of FMZ strategy #458201 "Multi EMA Crossover Momentum Strategy" (13, 30, 100 EMA Strategy with Rules).

FMZ source id: 458201

Source
    https://www.fmz.com/strategy/458201 (PineScript v5, FMZ last modified 2024-07-30 17:20:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 158-192), EMA 13 / 30 / 100 (constants)
    crossover(ema13, ema30) and ema13, ema30 > ema100 -> entry Buy;  crossunder and both < ema100 -> close Buy, entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close of the long on a sell signal comes with the short entry that reverses it, so it ends in
      a short (#437773). There is no other exit. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with a long-EMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458201_ema13_30_cross_ema100_side_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [13, 9],
    "slow": [30, 50],
    "trend": [100, 200],
}
DEFAULT_PARAMS = {"fast": 13, "slow": 30, "trend": 100}


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
    a, b, t = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("fast", "slow", "trend"))
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (a > t) & (b > t)
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (a < t) & (b < t)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
