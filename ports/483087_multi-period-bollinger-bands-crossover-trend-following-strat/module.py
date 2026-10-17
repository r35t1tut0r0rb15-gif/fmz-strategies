"""Closes below all three lower Bollinger bands (20, 120, 240) bought, closes above all three upper bands sold,
long only, 1-hour bars.
Port of FMZ strategy #483087 "多周期布林带交叉趋势跟踪策略-Multi-Period-Bollinger-Bands-Crossover-Trend-Following-Strategy" (Bollinger Bands Strategy (Buy Below, Sell Above)).

FMZ source id: 483087

Source
    https://www.fmz.com/strategy/483087 (PineScript v5, FMZ last modified 2025-02-27 17:02:33).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 92-130), BB 20 / 120 / 240, each x 2
    buy = close < lower20 and close < lower120 and close < lower240 -> entry long
    sell = close > upper20 and close > upper120 and close > upper240 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.stdev is the population standard deviation. Every bar in the condition is an entry signal (same-side ignored
      while held). Long only; the source has no shorts. No stops. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483087_triple_bollinger_extremes_long"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [2.0, 1.5],
    "len1": [20, 50],
}
DEFAULT_PARAMS = {"len1": 20, "len2": 120, "len3": 240, "mult": 2.0}


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
    below = pd.Series(True, index=c.index)
    above = pd.Series(True, index=c.index)
    for n in (int(p["len1"]), int(p["len2"]), int(p["len3"])):
        basis, dev = c.rolling(n).mean(), p["mult"] * c.rolling(n).std(ddof=0)
        below &= c < basis - dev
        above &= c > basis + dev
    false = pd.Series(False, index=bars_df.index)
    return below.astype(bool), above.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
