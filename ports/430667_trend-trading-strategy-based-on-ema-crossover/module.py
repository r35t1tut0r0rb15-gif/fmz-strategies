"""EMA 2 / 7 cross, 1-hour bars, long only: the EMA 2 crossing above the EMA 7 goes long, crossing below closes it.
Port of FMZ strategy #430667 "Trend Trading Strategy Based on EMA Crossover" (MP's Cloud Strat').

FMZ source id: 430667

Source
    https://www.fmz.com/strategy/430667 (PineScript v3, FMZ last modified 2023-10-31 14:37:38).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 197-325), EMA 2 / 7 (the ribbon EMAs only plot)
    buy_signal = crossover(ema(close, 2), ema(close, 7)) -> entry long
    sell_signal = crossunder(ema(close, 2), ema(close, 7)) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * ema3 uses len3, the "Long EMA" input (7). The fast / slow ribbon EMAs only plot. testPeriod()
      is always true.
    * Long only; Opposite entries cannot occur. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity per entry stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430667_ema2_7_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_ema": [2, 3],
    "long_ema": [7, 14],
}
DEFAULT_PARAMS = {"short_ema": 2, "long_ema": 7}


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
    f = c.ewm(span=int(p["short_ema"]), adjust=False).mean()
    s = c.ewm(span=int(p["long_ema"]), adjust=False).mean()
    xo = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    xu = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return xo, xu, false, false.copy()


def portfolio_kwargs(**params):
    return {}
