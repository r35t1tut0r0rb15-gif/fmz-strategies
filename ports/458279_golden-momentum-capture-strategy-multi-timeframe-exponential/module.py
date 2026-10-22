"""EMA 9 / 26 crossings on the side of the EMA 55, 1-hour bars: the cross up with the EMA 26 over the EMA 55 goes long, the cross down with it under goes short; reversing.
Port of FMZ strategy #458279 "Golden Momentum Capture Strategy Multi Timeframe Exponential Moving Average Crossover System" (Golden Crossover).

FMZ source id: 458279

Source
    https://www.fmz.com/strategy/458279 (PineScript v5, FMZ last modified 2024-07-31 15:00:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 195-234), EMA 9 / 26 / 55 (constants) by request.security on the chart's own time frame ('' inputs)
    crossover(ema9, ema26) and ema26 > ema55 -> entry Buy;  crossunder and ema26 < ema55 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The time-frame inputs default to '' (the chart), so the requests are the chart's own EMAs. There
      is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with a trend filter.
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

NAME = "fmz_458279_ema9_26_cross_ema55_side_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [26, 21],
    "trend": [55, 100],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 26, "trend": 55}


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
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (b > t)
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (b < t)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
