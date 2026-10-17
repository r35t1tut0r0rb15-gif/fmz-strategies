"""Four-SMA crosses, 1-hour bars: the SMA 20 crossing above the SMA 50 with the SMAs 20 > 50 > 100 > 200 stacked, or the
SMA 20 crossing above the SMA 100 while above the SMA 50, goes long; the SMA 20 crossing under the SMA 50 goes short.
Port of FMZ strategy #432114 "Simple Moving Average Crossover Strategy" (SMA crossover buy/sell [SCSM_Algo]).

FMZ source id: 432114

Source
    https://www.fmz.com/strategy/432114 (PineScript v5, FMZ last modified 2023-11-14 16:17:16).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 222-228), SMA 20 / 50 / 100 / 200
    crossover(sma20, sma50) and sma20 > sma50 and sma50 > sma100 and sma100 > sma200 or (crossover(sma20, sma100) and sma20 > sma50) -> entry long
    crossunder(sma20, sma50) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's "and" binds before "or", as written. The ma() helper and its type / colour inputs only
      draw lines (lines 230-268): not used by the orders.
    * strategy.entry reverses: REVERSAL INTENDED (always in once the first signal fires). FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the margin settings stored in original_sizing.txt.
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

NAME = "fmz_432114_four_sma_cross"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [20, 10],
    "len4": [200, 150],
}
DEFAULT_PARAMS = {"len1": 20, "len2": 50, "len3": 100, "len4": 200}


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
    s1, s2, s3, s4 = (c.rolling(int(p[k])).mean() for k in ("len1", "len2", "len3", "len4"))
    x12 = (s1 > s2) & (s1.shift(1) <= s2.shift(1))
    x13 = (s1 > s3) & (s1.shift(1) <= s3.shift(1))
    u12 = (s1 < s2) & (s1.shift(1) >= s2.shift(1))
    le = ((x12 & (s1 > s2) & (s2 > s3) & (s3 > s4)) | (x13 & (s1 > s2))).astype(bool)
    se = u12.astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
