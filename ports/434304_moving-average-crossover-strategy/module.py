"""Close crosses of the SMA 40, 1-hour bars, long only: a close crossing above the SMA goes long, a close crossing below it
closes the long.
Port of FMZ strategy #434304 "Moving Average Crossover Strategy" (MA Crossover (40)).

FMZ source id: 434304

Source
    https://www.fmz.com/strategy/434304 (PineScript v5, FMZ last modified 2023-12-05 11:52:28).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 125-146), SMA 40
    crossover(close, sma40) -> entry long;  crossunder(close, sma40) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only; an entry while long is ignored. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price against an average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434304_sma40_close_cross_long"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [40, 20, 80],
}
DEFAULT_PARAMS = {"sma_len": 40}


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
    s = c.rolling(int(p["sma_len"])).mean()
    le = ((c > s) & (c.shift(1) <= s.shift(1))).astype(bool)
    lx = ((c < s) & (c.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
