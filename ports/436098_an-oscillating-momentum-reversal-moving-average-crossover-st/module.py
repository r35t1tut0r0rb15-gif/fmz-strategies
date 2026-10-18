"""MACD histogram turns, 1-hour bars: a histogram that did not fall and sits at or over 0 goes long; one that did not rise and sits at or under 0 goes short
(reversing).
Port of FMZ strategy #436098 "An Oscillating Momentum Reversal Moving Average Crossover Strategy" (MACD Strategy by Sedkur).

FMZ source id: 436098

Source
    https://www.fmz.com/strategy/436098 (PineScript v4, FMZ last modified 2023-12-21 11:21:49).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 193-223), MACD 12 / 26 / 9 with EMAs; buy and sell histogram values 0.0
    hist = macd - signal;  entry long when hist[1] <= hist and buyh <= hist;  entry short when hist[1] >= hist and sellh >= hist   (year >= 2017)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are states re-sent every bar; vbt ignores a same-side signal. A flat histogram bar
      can satisfy both sides only if hist is exactly 0 (the short, sent last, stands). The year filter is the
      author's backtest window: dropped. strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, histogram turns.
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

NAME = "fmz_436098_macd_histogram_turn_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 21],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "buyh": 0.0, "sellh": 0.0}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    hist = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    le = ((hist.shift(1) <= hist) & (float(p["buyh"]) <= hist)).fillna(False)
    se = ((hist.shift(1) >= hist) & (float(p["sellh"]) >= hist)).fillna(False)
    se = se.astype(bool)
    le = (le & ~se).astype(bool)                       # both on one bar: the short, sent last, stands
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
