"""Normalised rate of change turns, 1-minute bars, long only: the 10-bar SMA of ROC 9 as a percentage of its 200-bar maximum rising for 3 bars while under -80 goes long; falling for 3 bars while over 80 closes.
Port of FMZ strategy #442221 "Rate of Change Optimization Strategy" (ROC).

FMZ source id: 442221

Source
    https://www.fmz.com/strategy/442221 (PineScript v5, FMZ last modified 2024-02-20 13:54:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 139-174), ROC 9; max history 200; smoothing 10; buy -80, sell 80
    roc = 100 (close - close[9]) / close[9];  pct = roc / highest(roc, 200) x 100;  s = sma(pct, 10);  rising(s, 3) and s < -80 -> entry Buy;  falling(s, 3) and s > 80 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * rising / falling (3) mean above (below) each of the 3 previous values. The ratio is ported as
      written (a negative 200-bar maximum flips its sign). Long only. No sizing code. FREQ = "1min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, normalised ROC turns.
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

NAME = "fmz_442221_normalised_roc_turn_long"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [9, 14],
    "max_history": [200, 100],
}
DEFAULT_PARAMS = {"length": 9, "max_history": 200, "smooth": 10, "buy_level": -80, "sell_level": 80}


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
    roc = 100 * (c - c.shift(n)) / c.shift(n)
    mx = roc.rolling(int(p["max_history"])).max()
    pct = roc / mx.where(mx != 0) * 100
    s = pct.rolling(int(p["smooth"])).mean()
    prev_max = pd.concat([s.shift(1), s.shift(2), s.shift(3)], axis=1).max(axis=1, skipna=False)
    prev_min = pd.concat([s.shift(1), s.shift(2), s.shift(3)], axis=1).min(axis=1, skipna=False)
    up = (s > prev_max) & (s < float(p["buy_level"]))
    dn = (s < prev_min) & (s > float(p["sell_level"]))
    false = pd.Series(False, index=c.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
