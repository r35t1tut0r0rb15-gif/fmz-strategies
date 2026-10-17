"""Noro's three-SMA alignment, 1-hour bars: the SMA 50 > 100 > 200 goes long, the reverse order goes short; the position
is kept otherwise.
Port of FMZ strategy #431911 "Williams Alligator Strategy" (Noro's Alligator Strategy by Bill Williams).

FMZ source id: 431911

Source
    https://www.fmz.com/strategy/431911 (PineScript v3, FMZ last modified 2023-11-13 10:58:22).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 185-232), SMA 50 / 100 / 200, lot 100 %
    up = sma50 > sma100 > sma200 -> entry long;  dn = sma50 < sma100 < sma200 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lot (capital % of equity, recomputed on a position change) is sizing. The 1900-2100 window
      is dropped. strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA alignment.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital % lot stored in original_sizing.txt.
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

NAME = "fmz_431911_three_sma_alignment"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [50, 20],
    "len3": [200, 100],
}
DEFAULT_PARAMS = {"len1": 50, "len2": 100, "len3": 200}


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
    s1, s2, s3 = (c.rolling(int(p[k])).mean() for k in ("len1", "len2", "len3"))
    up = ((s1 > s2) & (s2 > s3)).astype(bool)
    dn = ((s1 < s2) & (s2 < s3)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
