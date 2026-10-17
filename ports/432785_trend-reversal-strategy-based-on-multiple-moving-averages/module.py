"""M.H. Pee's trend detection index, long only, 5-minute bars: the 20-bar sum of 20-bar momentum crossing above the TDI
(|sum of momentum| - sum of |momentum| over 40 bars + over 20 bars) goes long; crossing back below it closes the long.
Port of FMZ strategy #432785 "Trend Reversal Strategy Based on Multiple Moving Averages" (M.H Pee indicators).

FMZ source id: 432785

Source
    https://www.fmz.com/strategy/432785 (PineScript v4, FMZ last modified 2023-11-21 14:53:48).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 205-334), indicator TDI (default), length 20
    mom = change(close, 20); tdi = |sum(mom, 20)| - sum(|mom|, 40) + sum(|mom|, 20); dir = sum(mom, 20)
    crossover(dir, tdi) -> entry long;  crossunder(dir, tdi) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the default indicator (TDI) is ported; TCF / TTF / TII are input options. The position
      size (equity and ATR based, possibly 0) is sizing (criterion 4). The date window (2016 to 2028)
      is dropped. Long only; Opposite entries cannot occur. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, momentum sums (both sides in price units, compared with each other).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity / ATR position size stored in original_sizing.txt.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432785_trend_detection_index_long"
FAMILY = "momentum_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 10, 40],
}
DEFAULT_PARAMS = {"length": 20}


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
    mom = c - c.shift(n)
    am = mom.abs()
    tdi = mom.rolling(n).sum().abs() - am.rolling(2 * n).sum() + am.rolling(n).sum()
    d = mom.rolling(n).sum()
    le = ((d > tdi) & (d.shift(1) <= tdi.shift(1))).astype(bool)
    lx = ((d < tdi) & (d.shift(1) >= tdi.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
