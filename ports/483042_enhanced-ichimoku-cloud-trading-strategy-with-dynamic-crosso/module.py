"""Ichimoku conversion 9 / base 26 crossings, hourly bars, long only: the up-cross goes long and the down-cross closes.
Port of FMZ strategy #483042 "Enhanced Ichimoku Cloud Trading Strategy with Dynamic Crossover Signals" (Ichimoku Cloud with Lables).

FMZ source id: 483042

Source
    https://www.fmz.com/strategy/483042 (PineScript v6, FMZ last modified 2025-02-21 10:41:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-140), conversion 9; base 26; span B 52; displacement 26 (plots only)
    crossover(conversion, base) -> entry LongTK;  crossunder(conversion, base) -> close LongTK

Interpretation choices (Pine rules in SURVEY_README.md)
    * The spans, cloud and labels are drawing only. Long only. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Tenkan / Kijun crossings.
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

NAME = "fmz_483042_tenkan9_kijun26_cross_long"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conversion_periods": [9, 7],
    "base_periods": [26, 22],
}
DEFAULT_PARAMS = {"conversion_periods": 9, "base_periods": 26}


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

    def mid(n):
        return (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2

    conv, base = mid(p["conversion_periods"]), mid(p["base_periods"])
    le = (conv > base) & (conv.shift(1) <= base.shift(1))
    lx = (conv < base) & (conv.shift(1) >= base.shift(1))
    false = pd.Series(False, index=h.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
