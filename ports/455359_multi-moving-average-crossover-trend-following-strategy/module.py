"""Tillson T3 (8, volume factor 0.7) turns, 1-hour bars: the T3 turning up goes long, turning down goes short; reversing.
Port of FMZ strategy #455359 "Multi Moving Average Crossover Trend Following Strategy" (Hashtag Signals and Backtest (Tillson T3 turns)).

FMZ source id: 455359

Source
    https://www.fmz.com/strategy/455359 (PineScript v4, FMZ last modified 2024-06-28 15:10:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 158-197), T3 length 8 of (h + l + 2c) / 4; volume factor 0.7
    crossover(T3, T3[1]) -> entry Long;  crossunder(T3, T3[1]) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The T3 is the six-fold EMA combination of (h + l + 2c) / 4 as written; its crossing of its own
      previous value is a turn. There is no exit: positions end at the opposite entry. REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, T3 turns.
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

NAME = "fmz_455359_tillson_t3_turn_reversal"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [8, 14],
    "vfactor": [0.7, 0.5],
}
DEFAULT_PARAMS = {"length": 8, "vfactor": 0.7}


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
    n = int(p["length"])
    a = float(p["vfactor"])
    x = (h + lo + 2 * c) / 4
    es = []
    cur = x
    for _ in range(6):
        cur = cur.ewm(span=n, adjust=False).mean()
        es.append(cur)
    e3, e4, e5, e6 = es[2], es[3], es[4], es[5]
    c1 = -a * a * a
    c2 = 3 * a * a + 3 * a * a * a
    c3 = -6 * a * a - 3 * a - 3 * a * a * a
    c4 = 1 + 3 * a + a * a * a + 3 * a * a
    t3 = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3
    t1, t2 = t3.shift(1), t3.shift(2)
    le = (t3 > t1) & (t1 <= t2)
    se = (t3 < t1) & (t1 >= t2)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
