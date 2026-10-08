"""Mechanical 16:00 long: the bar opening at 16:00 goes long, with a 0.4 % target and a 0.2 % stop.
Port of FMZ strategy #426779 "Mechanical Trading Strategy".

Source
    https://www.fmz.com/strategy/426779 (PineScript v4, FMZ last modified 2023-09-14 15:19:05).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 94-107), target 0.4 %, stop 0.2 %
    hour(time) == 16 -> entry long;
                        exit(limit = close * 1.004, stop = close * 0.998)   (that bar's close)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The hour is read in UTC (TradingView's Binance time zone; FMZ's is not documented:
      decision owed). On the 4h header bars, the 16:00 bar.
    * The levels are fractions of the signal bar's close; the port applies them to the fill
      price (tp_stop 0.004, sl_stop 0.002). The exit is re-issued with new levels at each later
      16:00 bar while the long is still open (a level that moves after entry): rule 2, mark
      trailing_stop_pending.
    * Long only. FREQ = "4h" from the backtest header; stops on 4h bars: coarse_bar_stop.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_426779_daily_1600_long_bracket"
FAMILY = "calendar_seasonal"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ENTRY_HOUR = 16  # UTC

GRID = {
    "tp_pct": [0.4, 1.0],
    "sl_pct": [0.2, 0.5],
}
DEFAULT_PARAMS = {"tp_pct": 0.4, "sl_pct": 0.2}


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
    idx = bars_df.index
    le = pd.Series(idx.tz_convert("UTC").hour == ENTRY_HOUR, index=idx)
    false = pd.Series(False, index=idx)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
