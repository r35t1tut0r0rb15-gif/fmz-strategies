"""Guarded channel breakouts, 1-hour bars: a close above the previous 26-bar high goes long when that high also tops the previous 10-bar high; a close under the previous 26-bar low goes short with the mirror
guard; reversing.
Port of FMZ strategy #437746 "Breakthrough Tracking Strategy" (BREAKOUT STRATEGY).

FMZ source id: 437746

Source
    https://www.fmz.com/strategy/437746 (PineScript v4, FMZ last modified 2024-01-05 12:00:25).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 94-116), price close, look back 26, guard 10, guard offset 1
    long = close > highest(26)[1] and highest(26)[1] > highest(10)[1];  short = close < lowest(26)[1] and lowest(26)[1] < lowest(10)[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * highest() / lowest() are of the high / low and include the current bar; both are read one bar back,
      as written. The guard is true only when the 26-bar extreme lies OUTSIDE the last 10 bars' range.
      REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG437746 (2 members, best partner #426597, Jaccard 0.801); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437746_guarded_hh_ll_breakout"
FAMILY = "donchian_breakout"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [26, 50],
    "guard": [10, 5],
}
DEFAULT_PARAMS = {"lookback": 26, "guard": 10, "guard_offset": 1}


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
    n, g, k = int(p["lookback"]), int(p["guard"]), int(p["guard_offset"])
    hh1 = h.rolling(n).max().shift(1)
    ll1 = lo.rolling(n).min().shift(1)
    lc = (c > hh1) & (hh1 > h.rolling(g).max().shift(k))
    sc = (c < ll1) & (ll1 < lo.rolling(g).min().shift(k))
    false = pd.Series(False, index=bars_df.index)
    return lc, false, sc, false.copy()


def portfolio_kwargs(**params):
    return {}
