""""Order block" sweeps, 4-hour bars: a low under the 5-bar low of 5 bars ago with the close over the close 5 bars ago goes long, a high over the 5-bar high of 5 bars ago with the close under the close 5 bars ago goes short; reversing.
Port of FMZ strategy #458184 "Multi Dimensional Order Flow Analysis and Trading Strategy" (Order Block Trading Strategy).

FMZ source id: 458184

Source
    https://www.fmz.com/strategy/458184 (PineScript v5, FMZ last modified 2024-07-30 16:32:52).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 169-205), lookback 5; threshold multiplier 1.0 on close[5]
    low < lowest(low, 5)[5] and close > close[5] x 1.0 -> entry Long;  high > highest(high, 5)[5] and close < close[5] x 1.0 -> entry Short
    long and bearish -> close Long;  short and bullish -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes come on the bars whose opposite entry already reverses the position, so they only
      repeat the reversals (#437773). There is no other exit. REVERSAL INTENDED. No sizing code. FREQ =
      "4h" from the backtest header (UTC-aligned 4-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, range sweeps with a close comparison.
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

NAME = "fmz_458184_order_block_sweep_close_compare_reversal"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [5, 10],
    "threshold": [1.0, 1.01],
}
DEFAULT_PARAMS = {"len": 5, "threshold": 1.0}


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
    n, t = int(p["len"]), float(p["threshold"])
    le = (lo < lo.rolling(n).min().shift(n)) & (c > c.shift(n) * t)
    se = (h > h.rolling(n).max().shift(n)) & (c < c.shift(n) * t)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
