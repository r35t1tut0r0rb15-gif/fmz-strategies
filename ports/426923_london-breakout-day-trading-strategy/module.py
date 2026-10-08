"""London breakout: on weekday bars opening 04:00-05:00, two rising closes after a dip go long and
two falling closes after a rise go short, each with a 0.5 % stop and target; any position still
open is closed at the first bar outside 03:00-09:00.
Port of FMZ strategy #426923 "London Breakout Day Trading Strategy".

Source
    https://www.fmz.com/strategy/426923 (PineScript v4, FMZ last modified 2023-09-15 15:43:04).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 152-279), session 0400-0500, close-out 0300-0900,
stop / target 0.005, Heikin-Ashi off, Monday-Friday on
    longC = close > close[1] and close[1] > close[2] and close[2] < close[3]  (shortC mirrors)
    in session on a weekday: longC -> entry long; shortC -> entry short
    exit(loss = close 0.005 / mintick, profit = the same) re-issued every bar
    not in 0300-0900 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Sessions and weekdays are read in UTC (TradingView's Binance time zone; FMZ's is not
      documented: decision owed); a bar is in a session when its open time is.
    * The bracket is 0.5 % of the close of the bar that re-issues it (a level that moves after
      entry): rule 2, mark trailing_stop_pending; the port fixes 0.5 % of the fill price.
    * Signals are emitted raw (entries on every qualifying bar, close-outs on every bar outside
      the hold window); the engine ignores those that do not apply, as Pine does.
    * The risk-based lot is sizing. strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "30min" from the backtest header.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_426923_london_breakout"
FAMILY = "calendar_seasonal"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
SESSION = (4 * 60, 5 * 60)       # "0400-0500", minutes of the UTC day, end exclusive
HOLD_WINDOW = (3 * 60, 9 * 60)   # "0300-0900"

GRID = {
    "sl": [0.005, 0.01],
    "tp": [0.005, 0.01],
}
DEFAULT_PARAMS = {"sl": 0.005, "tp": 0.005}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(target, index):
    """Signals from the position each bar's orders leave (1 / 0 / -1): a change to +-1 is an
    entry (reversing an opposite position), a change to 0 an exit of the side held."""
    m = len(target)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    prev = 0
    for i in range(m):
        n = target[i]
        if n != prev:
            if n == 1:
                le[i] = True
            elif n == -1:
                se[i] = True
            elif prev == 1:
                lx[i] = True
            else:
                sx[i] = True
        prev = n
    return tuple(pd.Series(x, index=index) for x in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    idx = bars_df.index.tz_convert("UTC")
    minute = idx.hour * 60 + idx.minute
    in_s = (minute >= SESSION[0]) & (minute < SESSION[1]) & (idx.dayofweek <= 4)
    in_hold = (minute >= HOLD_WINDOW[0]) & (minute < HOLD_WINDOW[1])
    c = bars_df["close"]
    c1, c2, c3 = c.shift(1), c.shift(2), c.shift(3)
    le = pd.Series(in_s & (c > c1) & (c1 > c2) & (c2 < c3), index=bars_df.index)
    se = pd.Series(in_s & (c < c1) & (c1 < c2) & (c2 > c3), index=bars_df.index)
    out = pd.Series(~np.asarray(in_hold), index=bars_df.index)
    # raw signals: after a stop or target the next session signal re-enters, as in Pine; the
    # close-out bars never coincide with entries (the session lies inside the hold window)
    return le, out, se, out.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl"], "tp_stop": p["tp"]}


def portfolio_kwargs(**params):
    return {}
