"""Ichimoku Tenkan / Kijun cross, 4-hour bars: the conversion line crossing above the base line goes long, crossing below
goes short.
Port of FMZ strategy #429786 "Ichimoku Lagging Cross Dual Line Trading Strategy" (Ichimoku Cloud Strategy v2.0).

FMZ source id: 429786

Source
    https://www.fmz.com/strategy/429786 (PineScript v4, FMZ last modified 2023-10-20 17:17:28).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 198-229), conversion 9, base 26 (the cloud and lagging span are drawn only)
    crossover(conversion, base) -> entry long; crossover(base, conversion) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * donchian(n) = (lowest low + highest high) / 2, current bar included. The lead lines and the lagging
      span are drawn only. strategy.entry reverses: REVERSAL INTENDED. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, line crosses from the bars only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND427806 (2 members, best partner #427806, Jaccard 0.658); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429786_ichimoku_tk_cross"
FAMILY = "ichimoku"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conv": [9, 7],
    "base": [26, 22],
}
DEFAULT_PARAMS = {"conv": 9, "base": 26}


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
    h, lo = bars_df["high"], bars_df["low"]
    don = lambda n: (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2  # noqa: E731
    t, k = don(p["conv"]), don(p["base"])
    long_e = ((t > k) & (t.shift(1) <= k.shift(1))).astype(bool)
    short_e = ((k > t) & (k.shift(1) <= t.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
