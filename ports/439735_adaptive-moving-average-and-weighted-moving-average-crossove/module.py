"""WMA 21 crossings of a five-times-nested EMA 14, 1-hour bars: the WMA crossing over the nested EMA goes long, crossing under goes short; reversing.
Port of FMZ strategy #439735 "Adaptive Moving Average and Weighted Moving Average Crossover Trading Strategy" (AIOMA-WMA Strategy).

FMZ source id: 439735

Source
    https://www.fmz.com/strategy/439735 (PineScript v5, FMZ last modified 2024-01-23 14:13:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 160-211), AIOMA 14 (five chained EMAs); WMA 21
    aioma = ema(ema(ema(ema(ema(close, 14), 14), 14), 14), 14);  cross_up = crossover(wma 21, aioma) -> entry Enter (long);  cross_down -> entry Exit (short)
    if cross_up and long: close Enter;  if cross_down and short: close Exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close tests read the position held before the bar: a cross up finds a short (the earlier
      cross down reversed into it), so the closes never act. strategy.entry reverses: REVERSAL INTENDED.
      No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, WMA / nested EMA crossings.
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

NAME = "fmz_439735_wma21_nested_ema14_cross"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "aioma_length": [14, 7],
    "wma_length": [21, 50],
}
DEFAULT_PARAMS = {"aioma_length": 14, "wma_length": 21}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["aioma_length"])
    a = c
    for _ in range(5):
        a = a.ewm(span=n, adjust=False).mean()
    w = _wma(c, int(p["wma_length"]))
    up = (w > a) & (w.shift(1) <= a.shift(1))
    dn = (w < a) & (w.shift(1) >= a.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
