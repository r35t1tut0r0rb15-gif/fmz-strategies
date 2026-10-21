"""Percent-rank level crossings, 4-hour bars: the 10-bar percent rank of the close minus 50 crossing over +30 goes long (and closes a short), crossing under -30 goes short (and closes a long); reversing.
Port of FMZ strategy #437383 "Parameter Optimized Trend Following Quantitative Strategy" (percentrank).

FMZ source id: 437383

Source
    https://www.fmz.com/strategy/437383 (PineScript v4, FMZ last modified 2024-01-02 11:01:22).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 130-153), lookback 10, scale offset 50, levels +30 / -30
    prank = percentrank(close, 10) - 50;  crossunder(30, prank) -> entry Long, close Short;  crossover(-30, prank) -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * percentrank(src, n) = the share of the previous n values at or below the current one, in percent
      (na until n earlier values exist). A cross of a constant line by prank is prank crossing it. Orders
      follow the script's call order; the result is a reversal at each level crossing. REVERSAL INTENDED.
      No sizing code. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, percent rank levels.
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

NAME = "fmz_437383_percent_rank_level_cross"
FAMILY = "momentum_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20],
    "level": [30.0, 20.0],
}
DEFAULT_PARAMS = {"length": 10, "level": 30.0, "scale": 50.0}


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
    cnt = sum((c.shift(i) <= c).astype(float) for i in range(1, n + 1))
    pr = (cnt / n * 100.0).where(c.shift(n).notna()) - float(p["scale"])
    lv = float(p["level"])
    pr1 = pr.shift(1)
    up = (pr > lv) & (pr1 <= lv)
    dn = (pr < -lv) & (pr1 >= -lv)
    return up, dn, dn, up.copy()


def portfolio_kwargs(**params):
    return {}
