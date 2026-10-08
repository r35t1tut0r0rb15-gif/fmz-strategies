"""Buy Monday, exit Wednesday, long only: the Monday bar opening inside 14:00-16:01 goes long, the
Wednesday bar in that window closes the long; a 4 % stop and a 3 % target run meanwhile.
Port of FMZ strategy #426511 "Buy Monday Sell Wednesday Trading Strategy".

Source
    https://www.fmz.com/strategy/426511 (PineScript v5, FMZ last modified 2023-09-12 16:44:53).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 112-127), SL 4 %, TP 3 %
    isLong = dayofweek == monday and not na(time(timeframe.period, "1400-1601"))
    isExit = dayofweek == wednesday and not na(time(timeframe.period, "1400-1601"))
    entry long when isLong; while long: close when isExit, exit(stop = avg * 0.96, limit = avg * 1.03)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The session and the weekday are read in UTC (the exchange time zone TradingView uses for
      Binance; FMZ's is not documented: decision owed). A bar is in the session when its open
      time is in [14:00, 16:01): on the 4h header bars, the 16:00 bar.
    * strategy.close("Enter Long", isExit): the second positional argument is `when` in the
      Pine v5 of the source's date (later releases moved `comment` there); read as `when`.
    * Stop / target are fractions of the fill price (sl_stop / tp_stop). Entries repeat only on
      one bar a week and are ignored while long, so nothing needs mirroring.
    * Long only (no short entry). FREQ = "4h" from the backtest header; stops on 4h bars:
      coarse_bar_stop.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_426511_monday_wednesday_swing"
FAMILY = "calendar_seasonal"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
SESSION = (14 * 60, 16 * 60 + 1)  # "1400-1601", minutes of the UTC day, end exclusive

GRID = {
    "sl_pct": [2.0, 4.0],
    "tp_pct": [3.0, 5.0],
}
DEFAULT_PARAMS = {"sl_pct": 4.0, "tp_pct": 3.0}


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
    idx = bars_df.index.tz_convert("UTC")
    minute = idx.hour * 60 + idx.minute
    in_session = (minute >= SESSION[0]) & (minute < SESSION[1])
    le = pd.Series(in_session & (idx.dayofweek == 0), index=bars_df.index)
    lx = pd.Series(in_session & (idx.dayofweek == 2), index=bars_df.index)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
