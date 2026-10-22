"""Fibonacci-lag average candles, long only, 1-hour bars: each price is the mean of its values 0, 1, 2, 3, 5, 8, 13, 21, 34 and 55 bars back; a green average candle with two rising closes and highs above the
mean of nine EMAs of the average close goes long; a red one with two falling closes and lows under it closes.
Port of FMZ strategy #439350 "基于斐波那契平均K线和移动平均线的量化交易策略Fibonacci-Average-Candle-with-Moving-Average-Strategy-for-Quantitative-Trading" (Fibonacci candle).

FMZ source id: 439350

Source
    https://www.fmz.com/strategy/439350 (PineScript v4, FMZ last modified 2024-01-19 14:36:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 134-174), no inputs; lags 0 1 2 3 5 8 13 21 34 55; EMAs 1 2 3 5 8 13 21 34 55 of the average close
    avg_x = (x + x[1] + x[2] + x[3] + x[5] + x[8] + x[13] + x[21] + x[34] + x[55]) / 10;  avg_ema = mean of ema(avg_close, 55 / 1 / 2 / 3 / 5 / 8 / 13 / 21 / 34)
    long = avg_open < avg_close and two rising avg closes and highs;  entry long when long and avg_close > avg_ema;  close long when short and avg_close < avg_ema

Interpretation choices (Pine rules in SURVEY_README.md)
    * The averages use past bars only. The entry and the close cannot share a bar (candle colours).
      Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, lagged price averages and EMAs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439350_fibonacci_average_candle_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slow_ema": [55, 89],
}
DEFAULT_PARAMS = {"slow_ema": 55}

LAGS = (0, 1, 2, 3, 5, 8, 13, 21, 34, 55)
EMAS = (1, 2, 3, 5, 8, 13, 21, 34)


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

    def avg(x):
        return sum(x.shift(k) for k in LAGS) / len(LAGS)

    ao, ah, al, ac = (avg(bars_df[k]) for k in ("open", "high", "low", "close"))
    spans = (int(p["slow_ema"]),) + EMAS
    ae = sum(ac.ewm(span=s, adjust=False).mean() for s in spans) / len(spans)
    long_ = ((ao < ac) & (ac > ac.shift(1)) & (ah > ah.shift(1)) & (ac.shift(1) > ac.shift(2))
             & (ah.shift(1) > ah.shift(2)))
    short_ = ((ao > ac) & (ac < ac.shift(1)) & (al < al.shift(1)) & (ac.shift(1) < ac.shift(2))
              & (al.shift(1) < al.shift(2)))
    false = pd.Series(False, index=bars_df.index)
    return long_ & (ac > ae), short_ & (ac < ae), false, false.copy()


def portfolio_kwargs(**params):
    return {}
