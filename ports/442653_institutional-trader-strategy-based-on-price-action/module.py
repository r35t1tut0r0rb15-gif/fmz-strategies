""""Order blocks" against an SMA 60 fair value, 3-hour bars: the close within 0.382 of the 20-bar range above the fair value goes long; any close under the fair value goes short (the range test then always
holds); reversing.
Port of FMZ strategy #442653 "Institutional Trader Strategy Based on Price Action" (ICT Strategy).

FMZ source id: 442653

Source
    https://www.fmz.com/strategy/442653 (PineScript v5, FMZ last modified 2024-02-23 15:04:39).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 153-186), order block length 20; fair value SMA 60
    isOrderBlock = (close - fairValue) <= 0.382 (highest(high, 20) - lowest(low, 20));  isOrderBlock and close > fairValue -> entry Buy;  isOrderBlock and close < fairValue -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The difference is signed, as written, so every close under the fair value passes the test. The
      entries are level tests, refused while held. strategy.entry reverses: REVERSAL INTENDED. No sizing
      code. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close vs SMA with a range test.
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

NAME = "fmz_442653_fair_value_range_block_reversal"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "fair_value_period": [60, 120],
}
DEFAULT_PARAMS = {"length": 20, "fair_value_period": 60, "frac": 0.382}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    fv = c.rolling(int(p["fair_value_period"])).mean()
    block = (c - fv) <= float(p["frac"]) * (h.rolling(n).max() - lo.rolling(n).min())
    le = block & (c > fv)
    se = block & (c < fv)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
