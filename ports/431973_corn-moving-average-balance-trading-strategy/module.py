"""EMA 20 / 100 crosses, 1-hour bars: the EMA 20 crossing above the EMA 100 goes long, crossing below goes short (the default
Long+Short mode).
Port of FMZ strategy #431973 "Corn Moving Average Balance Trading Strategy" (MASelect Crossover Strat).

FMZ source id: 431973

Source
    https://www.fmz.com/strategy/431973 (PineScript v3, FMZ last modified 2023-11-13 18:00:09).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 144-184), active EMA 20, base EMA 100, Long+Short
    co = crossover(ma1, ma2) -> entry long;  cu = crossunder(ma1, ma2) -> entry short (Long+Short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default MA types are EMA (the VWMA option, which would use volume, is off). strategy.entry
      reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
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

NAME = "fmz_431973_ema_20_100_cross"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [20, 10],
    "len2": [100, 50],
}
DEFAULT_PARAMS = {"len1": 20, "len2": 100}


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
    a = c.ewm(span=int(p["len1"]), adjust=False).mean()
    b = c.ewm(span=int(p["len2"]), adjust=False).mean()
    up = ((a > b) & (a.shift(1) <= b.shift(1))).astype(bool)
    dn = ((a < b) & (a.shift(1) >= b.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
