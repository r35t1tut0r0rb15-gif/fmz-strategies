"""Bollinger band touches, 1-hour bars: the close at or under the lower band (20, 2) goes long, at or over the upper band goes short; reversing.
Port of FMZ strategy #442116 "基于RSI布林带和支撑阻力策略Rational-Trading-Robot-Powered-by-RSI-Strategy" (RSI, Bollinger Bands, and Support/Resistance Trading Bot).

FMZ source id: 442116

Source
    https://www.fmz.com/strategy/442116 (PineScript v4, FMZ last modified 2024-02-19 14:43:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 143-213), RSI 14 (70 / 30, unused by the orders); BB 20 / 2; support / resistance = the bands
    long = close <= lower and low <= support (= lower) -> entry Long;  short = close >= upper and high >= resistance (= upper) -> entry Short;  a held position is closed first when the opposite condition fires

Interpretation choices (Pine rules in SURVEY_README.md)
    * The support and resistance lines are the bands, so the extra tests are implied. The RSI condition
      and the basis-cross exits are only plotted (arrows), never ordered. The close before an opposite
      entry and the entry make one reversal. Pine's stdev is the population deviation. The conditions are
      levels; an entry while already in that direction does nothing. REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger touches.
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

NAME = "fmz_442116_bb_touch_level_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_length": [20, 50],
    "bb_mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"bb_length": 20, "bb_mult": 2.0}


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
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    le = (c <= dn) & (lo <= dn)
    se = (c >= up) & (h >= up)
    false = pd.Series(False, index=c.index)
    return le, false, se & ~le, false.copy()


def portfolio_kwargs(**params):
    return {}
