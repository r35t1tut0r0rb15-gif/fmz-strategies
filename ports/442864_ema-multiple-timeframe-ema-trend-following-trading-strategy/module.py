"""EMA 12 / 15 / 18 / 21 / 24 ribbon order, 1-hour bars: the ribbon stacked upward holds long, downward holds short; reversing.
Port of FMZ strategy #442864 "多周期EMA顺势突破交易策略Multiple-Timeframe-EMA-Trend-Following-Trading-Strategy" (Scalping Strategy - EMA (EMA Scalp)).

FMZ source id: 442864

Source
    https://www.fmz.com/strategy/442864 (PineScript v5, FMZ last modified 2024-02-26 16:55:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 164-202), EMA 12 / 15 / 18 / 21 / 24; start date (isAfterStartDate true)
    ema12 > ema15 > ema18 > ema21 > ema24 -> entry Buy;  the reverse order -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The start-date filter is set to true in the source. The entries are level tests, refused while
      held. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stacked EMA ribbon.
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

NAME = "fmz_442864_ema12_24_ribbon_order_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "start": [12, 6],
    "step": [3, 5],
}
DEFAULT_PARAMS = {"start": 12, "step": 3}


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
    s0, st = int(p["start"]), int(p["step"])
    e = [c.ewm(span=s0 + st * k, adjust=False).mean() for k in range(5)]
    up = pd.Series(True, index=c.index)
    dn = pd.Series(True, index=c.index)
    for a, b in zip(e[:-1], e[1:]):
        up &= a > b
        dn &= a < b
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
