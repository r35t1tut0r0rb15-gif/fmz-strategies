"""Hourly bars: a close crossing over the top of the undisplaced Ichimoku cloud (9 / 26 / 52) goes long; an SMA 14 / 28 down-cross goes short; each entry reverses the other.
Port of FMZ strategy #488518 "Dynamic Kumo Breakout Quantitative Trading Strategy" (KumoBreakLong).

FMZ source id: 488518

Source
    https://www.fmz.com/strategy/488518 (PineScript v6, FMZ last modified 2025-03-28 15:16:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 201-239), Tenkan 9; Kijun 26; Senkou B 52 (not displaced); SMA 14 / 28
    crossover(close, max(senkouA, senkouB)) -> entry Long;  crossunder(sma14, sma28) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cloud is the current (undisplaced) spans, as written. The exit condition (a close under the
      cloud bottom) is computed but never used. No other exits: each entry reverses the other (REVERSAL
      INTENDED). No sizing code. MPL 2.0 source (the notice is kept: Mozilla Public License 2.0,
      © SwissyTrader). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku cloud breakouts with an SMA-cross short side.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
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

NAME = "fmz_488518_kumo_top_breakout_long_sma14_28_cross_short_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lenKijun": [26, 20],
    "lenSenkou": [52, 40],
}
DEFAULT_PARAMS = {"lenKijun": 26, "lenSenkou": 52, "lenTenkan": 9}


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

    def mid(n):
        return (h.rolling(int(n)).max() + lo.rolling(int(n)).min()) / 2

    a = (mid(p["lenTenkan"]) + mid(p["lenKijun"])) / 2
    b = mid(p["lenSenkou"])
    top = pd.concat([a, b], axis=1).max(axis=1, skipna=False)
    le = (c > top) & (c.shift(1) <= top.shift(1))
    f, s = c.rolling(14).mean(), c.rolling(28).mean()
    se = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
