"""Turnaround Monday, 1-hour bars, long only: a Monday bar (UTC calendar day) closing below the previous close, which itself
closed below the one before, goes long; a close above the previous bar's high closes the long.
Port of FMZ strategy #431263 "Monday Reversal Intraday Trend Following Strategy" (ET Forex TurnaroundMonday).

FMZ source id: 431263

Source
    https://www.fmz.com/strategy/431263 (PineScript v4, FMZ last modified 2023-11-06 15:34:06).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 194-242), deltaDay 0, from 2018
    EntryLong = dayofweek == monday and close < close[1] and close[1] < close[2] -> entry "ETLong"
    ExitLong = long and close > high[1] -> close "ETLong"  (written before the entry)

Interpretation choices (Pine rules in SURVEY_README.md)
    * dayofweek is the exchange time of the bar's open (UTC on Binance): a Monday is a UTC calendar
      Monday (UTC, no DST; not a venue open). The time window, hold time and hour shifts are
      commented out; the 2018 start is dropped.
    * Entry and exit cannot meet on one bar (a close below close[1] is not above high[1]). The
      money-management lot (capital / close) is sizing. Long only; Opposite entries cannot occur.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, weekday and close comparisons.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital / close lot stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: UTC calendar Monday (exchange time on Binance; UTC, no DST); not a venue open.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431263_turnaround_monday_long"
FAMILY = "calendar_seasonal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "down_bars": [2, 1],
    "weekday": [0, 1],
}
DEFAULT_PARAMS = {"down_bars": 2, "weekday": 0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, c = bars_df["high"], bars_df["close"]
    wd = bars_df.index.tz_convert("UTC").weekday == int(p["weekday"])
    down = pd.Series(True, index=c.index)
    for k in range(int(p["down_bars"])):
        down &= c.shift(k) < c.shift(k + 1)
    entry = (wd & down.to_numpy())
    out = (c > h.shift(1)).to_numpy()
    m = len(entry)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 1 and out[i]:
            pos = 0
        if entry[i]:
            pos = 1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
