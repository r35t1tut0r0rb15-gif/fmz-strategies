"""Hourly bars: the SMA 14 crossing over the SMA 28 goes long, crossing under goes short; reversing. The "W pattern on high volume" entry can never fire.
Port of FMZ strategy #440538 "量化W形态高手之路Quant-W-Pattern-Master-Strategy" (Combined Strategy (W pattern + SMA 14 / 28)).

FMZ source id: 440538

Source
    https://www.fmz.com/strategy/440538 (PineScript v5, FMZ last modified 2024-01-31 14:49:56).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 177-208), W pattern: SMA 10 / 30, volume x 2 over SMA 20; second strategy SMA 14 / 28
    wBottom = crossover(sma10, sma30) and crossover(sma10[1], sma30[1]);  wBottom and volume > 2 x sma(volume, 20) -> entry W Pattern Buy
    crossover(sma14, sma28) -> entry Long Entry;  crossunder -> entry Short Entry

Interpretation choices (Pine rules in SURVEY_README.md)
    * wBottom needs two crossovers on consecutive bars, which cannot happen (the second requires the
      fast average to be below on the bar the first left it above), so the W / volume entry never fires
      and volume feeds nothing (weird case; held for volume, not used). REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA 14 / 28 crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440538_sma14_28_cross_dead_w_pattern_1h_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [14, 10],
    "slow": [28, 50],
}
DEFAULT_PARAMS = {"fast": 14, "slow": 28}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return up.astype(bool), false, dn.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
