"""Three Bollinger bands (20 / 120 / 240, 2 sd), hourly bars, long only: a close under all three lower bands goes long, a close over all three upper bands closes.
Port of FMZ strategy #483087 "Multi Period Bollinger Bands Crossover Trend Following Strategy" (Bollinger Bands Strategy (Buy Below, Sell Above)).

FMZ source id: 483087

Source
    https://www.fmz.com/strategy/483087 (PineScript v5, FMZ last modified 2025-02-27 17:02:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-144), Bollinger 20 / 120 / 240, each 2.0
    close < lower20 and close < lower120 and close < lower240 -> entry Buy;  close > upper20 and > upper120 and > upper240 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both conditions are states; a repeat entry while long adds nothing. Long only. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, three Bollinger bands at once.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483087_bb20_120_240_all_lower_buy_all_upper_exit_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length1": [20, 10],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length1": 20, "mult": 2.0, "length2": 120, "length3": 240}


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
    k = float(p["mult"])
    below = pd.Series(True, index=c.index)
    above = pd.Series(True, index=c.index)
    for key in ("length1", "length2", "length3"):
        n = int(p[key])
        b, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
        below = below & (c < b - k * sd)
        above = above & (c > b + k * sd)
    false = pd.Series(False, index=c.index)
    return below, above & ~below, false, false.copy()


def portfolio_kwargs(**params):
    return {}
