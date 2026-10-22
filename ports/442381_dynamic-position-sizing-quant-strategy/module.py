"""SMA 14 / 28 crossings, 1-hour bars: the SMA 14 crossing over the SMA 28 goes long, crossing under goes short; reversing (the compounding quantity is sizing).
Port of FMZ strategy #442381 "Dynamic Position Sizing Quant Strategy" (Tendies Heist Auto Compounding Example).

FMZ source id: 442381

Source
    https://www.fmz.com/strategy/442381 (PineScript v4, FMZ last modified 2024-02-21 14:52:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 147-177), SMA 14 / 28; leverage 10000, max position size 25 (auto-compounding quantity)
    crossover(sma14, sma28) -> entry Long (qty = size);  crossunder -> entry Short (qty = size);  size steps up / down by 1 with equity / 10000, capped at 25

Interpretation choices (Pine rules in SURVEY_README.md)
    * The quantity rule (size from equity / 10000, capped by strategy.risk.max_position_size(25)) is
      sizing, not signal logic. strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the compounding quantity rule and position cap stored.
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

NAME = "fmz_442381_sma14_28_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [14, 9],
    "slow": [28, 50],
}
DEFAULT_PARAMS = {"fast": 14, "slow": 28}


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
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
