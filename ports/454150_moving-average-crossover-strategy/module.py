"""SMA 9 / 21 crossings, 5-minute bars: the cross up goes long, the cross down goes short; reversing.
Port of FMZ strategy #454150 "Moving Average Crossover Strategy" (Moving Average Crossover Strategy (SMA 9 / 21, 5 minutes)).

FMZ source id: 454150

Source
    https://www.fmz.com/strategy/454150 (PineScript v5, FMZ last modified 2024-06-14 15:48:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-140), SMA 9 / 21; quantity 1 % of a 100 balance over the bar range, x 1.1 / 0.9 by net profit
    crossover(sma9, sma21) -> entry Buy (qty);  crossunder -> entry Sell (qty)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The quantity (risk over the bar's range, scaled by the sign of the net profit) only sizes the
      orders: sizing, stored. There is no exit: positions end at the opposite entry. REVERSAL
      INTENDED. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the range-based quantity stored.
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

NAME = "fmz_454150_sma9_21_cross_5m_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21}


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
    le = (f > s) & (f.shift(1) <= s.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
