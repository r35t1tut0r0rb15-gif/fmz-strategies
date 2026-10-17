"""Ichimoku tenkan / kijun crosses, long only, 1-hour bars: the 9-bar Donchian mid line crossing above the 26-bar mid
line goes long; crossing below closes it.
Port of FMZ strategy #483042 "市云转向指标改良型多空交叉交易策略-Enhanced-Ichimoku-Cloud-Trading-Strategy-with-Dynamic-Crossover-Signals" (Ichimoku Cloud with Lables).

FMZ source id: 483042

Source
    https://www.fmz.com/strategy/483042 (PineScript v6, FMZ last modified 2025-02-21 10:41:00).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 93-139), conversion 9, base 26 (spans and lagging line only plotted)
    long = crossover(conversion, base) -> entry long; close = crossunder(conversion, base) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * donchian(len) = average of the lowest low and highest high over len bars. Long only; the source has no shorts.
      No stops. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Donchian mid lines.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483042_tenkan_kijun_cross_long"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conversion": [9, 7],
    "base": [26, 22],
}
DEFAULT_PARAMS = {"conversion": 9, "base": 26}


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
    conv = (h.rolling(int(p["conversion"])).max() + lo.rolling(int(p["conversion"])).min()) / 2
    base = (h.rolling(int(p["base"])).max() + lo.rolling(int(p["base"])).min()) / 2
    long_e = ((conv > base) & (conv.shift(1) <= base.shift(1))).astype(bool)
    long_x = ((conv < base) & (conv.shift(1) >= base.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
