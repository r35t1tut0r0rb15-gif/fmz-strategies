"""Mid-range line crossings, 1-hour bars, long only: the average of the 10- and 16-bar high-low ranges' mid-points crossing over the average of the 20- and 10-bar ones goes long, crossing back under closes.
Port of FMZ strategy #440510 "Bitcoin Trading Strategy Based on Ichimoku Cloud" (BTC_ISHIMOKU).

FMZ source id: 440510

Source
    https://www.fmz.com/strategy/440510 (PineScript v4, FMZ last modified 2024-01-31 11:06:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 162-191), periods 20 / 10 / 16; years 2020-2025
    HL1 = (highest(high, 20) + lowest(low, 20) + highest(high, 10) + lowest(low, 10)) / 4;  HL2 = (highest(high, 10) + lowest(low, 10) + highest(high, 16) + lowest(low, 16)) / 4
    crossover(HL2, HL1) and in years -> entry Long;  crossunder(HL2, HL1) and in years -> close Long;  (the short entry is commented out)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The author's bounded 2020-2025 window is dropped. Long only. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, range mid-point lines.
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

NAME = "fmz_440510_range_midline_cross_long"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period_max": [20, 52],
    "period_min": [16, 26],
}
DEFAULT_PARAMS = {"period_max": 20, "period_min": 16, "period_med": 10}


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

    def mid2(n):
        return h.rolling(n).max() + lo.rolling(n).min()

    a, b, d = mid2(int(p["period_max"])), mid2(int(p["period_med"])), mid2(int(p["period_min"]))
    hl1 = (a + b) / 4
    hl2 = (b + d) / 4
    up = (hl2 > hl1) & (hl2.shift(1) <= hl1.shift(1))
    dn = (hl2 < hl1) & (hl2.shift(1) >= hl1.shift(1))
    false = pd.Series(False, index=h.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
