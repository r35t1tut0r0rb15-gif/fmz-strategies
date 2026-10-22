"""Re-entries into the one-sd Bollinger band (20), 2-hour bars: a close rising back over SMA - 1 sd goes long, a close falling back under SMA + 1 sd goes short; reversing (the 2-sd band only plots).
Port of FMZ strategy #449947 "Bollinger Bands Double Standard Deviation Filtering 5 Minute Quantitative Trading Strategy" (Five Min Scalping Strategy (Bollinger 1 / 2 sd)).

FMZ source id: 449947

Source
    https://www.fmz.com/strategy/449947 (PineScript v5, FMZ last modified 2024-04-30 16:03:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-144), SMA 20; bands 1 sd (trades) and 2 sd (plot only)
    close[1] < lower1 and close > lower1 -> entry Long, close Short;  close[1] > upper1 and close < upper1 -> entry Short, close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bands' previous values are not used: the test compares the previous close with the current
      band, as written. Each close comes with the opposite entry on the same bar: one reversal. Pine's
      stdev is the population deviation. REVERSAL INTENDED. No sizing code. FREQ = "2h" from the
      backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, one-sd band re-entries.
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

NAME = "fmz_449947_one_sd_band_reentry_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "k": [1.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "k": 1.0}


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
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    lower = basis - float(p["k"]) * sd
    upper = basis + float(p["k"]) * sd
    c1 = c.shift(1)
    le = (c1 < lower) & (c > lower)
    se = (c1 > upper) & (c < upper)
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
