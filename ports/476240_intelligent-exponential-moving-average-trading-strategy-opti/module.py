"""Close crossings of the EMA 9 on the side of the EMA 9 / 21 trend, 45-minute bars: the cross up in an up-trend goes long, the cross down in a down-trend goes short; the opposite close crossing closes; reversing.
Port of FMZ strategy #476240 "Intelligent Exponential Moving Average Trading Strategy Optimization System" (Smart EMA Algo).

FMZ source id: 476240

Source
    https://www.fmz.com/strategy/476240 (PineScript v6, FMZ last modified 2024-12-27 13:56:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-138), EMA 9 / 21; source close
    ema9 > ema21 and crossover(close, ema9) -> entry Buy;  ema9 < ema21 and crossunder(close, ema9) -> entry Sell;  crossunder(close, ema9) -> close Buy;  crossover(close, ema9) -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * A close acts only on the held position; a close written after a reversing entry on the same bar
      leaves the reversal standing (as #441963). REVERSAL INTENDED. No sizing code. FREQ = "45min" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA close crossings with an EMA trend filter.
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

NAME = "fmz_476240_close_cross_ema9_ema21_trend_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_short": [9, 5],
    "ema_long": [21, 50],
}
DEFAULT_PARAMS = {"ema_short": 9, "ema_long": 21}


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
    es = c.ewm(span=int(p["ema_short"]), adjust=False).mean()
    el = c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    up = (c > es) & (c.shift(1) <= es.shift(1))
    dn = (c < es) & (c.shift(1) >= es.shift(1))
    le = (es > el) & up
    se = (es < el) & dn
    return le, dn & ~se, se, up & ~le


def portfolio_kwargs(**params):
    return {}
