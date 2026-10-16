"""SMA 10 / SMA 20 cross with a trend filter on longs, 3-hour bars: the up cross with the close above the SMA
200 goes long, every down cross goes short.
Port of FMZ strategy #428814 "Moving Average Crossover Strategy" (GMS: Moving Average Crossover Strategy).

FMZ source id: 428814

Source
    https://www.fmz.com/strategy/428814 (PineScript v4, FMZ last modified 2023-10-09 17:03:23).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 186-665), defaults Both / SMA / SMA / 10 / 20 / Above / 200
    (LongShort "Both", AboveBelow "Above", MAs SMA and SMA: the branch at lines 663-665)
    crossover(sma(close,10), sma(close,20)) and close > sma(close,200) -> entry long
    crossunder(sma(close,10), sma(close,20)) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the default branch is ported; the other 47 branches are input options (other MA types,
      filters and sides).
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crosses only.
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

NAME = "fmz_428814_sma10_20_cross_trend_long"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1": [10, 5],
    "ma2": [20, 40],
}
DEFAULT_PARAMS = {"ma1": 10, "ma2": 20, "trend_length": 200}


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
    f, s = c.rolling(int(p["ma1"])).mean(), c.rolling(int(p["ma2"])).mean()
    t = c.rolling(int(p["trend_length"])).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (c > t)).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
