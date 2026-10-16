"""Integrated distance from the SMA 170, 1-minute bars: the sum of (close - SMA 170) over the last 30 bars above zero
holds a long, below zero holds a short.
Port of FMZ strategy #429484 "Momentum Tracking Strategy Based on Indicator Integration" (Indicator Integrator Strat).

FMZ source id: 429484

Source
    https://www.fmz.com/strategy/429484 (PineScript v2, FMZ last modified 2023-10-17 15:26:49).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 182-218), SMA 170, summation 29 (30 terms)
    sum = k[0] + k[1] + ... + k[29], k = close - sma(close,170)
    sum > 0 -> entry long (close short); sum < 0 -> entry short (close long)
    TP / SL / trail inputs 0 -> na (off)

Interpretation choices (Pine rules in SURVEY_README.md)
    * `for i = 0 to s` with s = 29 adds 30 terms (the current bar included). The sum is in price units;
      only its sign is used.
    * The take-profit / stop / trail inputs default to 0, i.e. na: the strategy.exit calls place nothing.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, the sign of a sum only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and the off-by-default exits stored.
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

NAME = "fmz_429484_integrated_sma_distance"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [170, 100],
    "terms": [30, 15],
}
DEFAULT_PARAMS = {"length": 170, "terms": 30}


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
    k = c - c.rolling(int(p["length"])).mean()
    s = k.rolling(int(p["terms"])).sum()
    long_e = (s > 0).astype(bool)
    short_e = (s < 0).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
