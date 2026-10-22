"""The 09:15 UTC 1-minute candle's range, once a day: from 10:00 a close over its high goes long, under its low goes short; a close back through a 1.5-range trail of closes closes, and 15:30 closes everything.
Port of FMZ strategy #489018 "First Candle Breakout Dynamic Trailing Stop EOD Close Strategy" (First Candle Breakout - Trailing Stop & EOD Close).

FMZ source id: 489018

Source
    https://www.fmz.com/strategy/489018 (PineScript v5, FMZ last modified 2025-04-01 11:06:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 160-222), first candle 09:15; trail 1.5 x its range; close-all 15:30
    09:15 -> first high / low := the bar's, taken := false, direction := 0, trail := na
    hour > 9 and not taken and close > first high -> entry Buy, trail := close - 1.5 range, taken;  mirror -> entry Sell
    long: trail := max(trail, close - 1.5 range), close <= trail -> close Buy;  short mirror;  taken and 15:30 -> close all

Interpretation choices (Pine rules in SURVEY_README.md)
    * hour / minute on the Binance header read UTC, at each bar's opening time. The trail is a ratchet of
      closes tested on closes and sent as a close (an exit signal, no stop module), followed in a loop, as
      written; it is not cleared after an exit, so later closes beyond it close nothing. One entry per day
      (reset at 09:15); a position opened late in the day can still be open when the next day's opposite
      entry comes, which reverses it (REVERSAL INTENDED). No sizing code. FREQ = "1min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested trail and clock close.
    2 generic: PASS, first-candle range breakouts with a range trail.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: first candle 09:15, entries from 10:00, close-all 15:30 UTC (bar opening times).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489018_first_candle_0915_breakout_close_trail_1530_close"
FAMILY = "opening_range_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "trailStopMultiplier": [1.5, 3.0],
    "endHour": [15, 20],
}
DEFAULT_PARAMS = {"trailStopMultiplier": 1.5, "endHour": 15, "startHour": 9, "startMinute": 15, "endMinute": 30}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    idx = c.index.tz_convert("UTC")
    hr, mn = np.asarray(idx.hour), np.asarray(idx.minute)
    hv, lv, cv = (x.to_numpy(dtype=float) for x in (h, lo, c))
    sh, sm = int(p["startHour"]), int(p["startMinute"])
    eh, em = int(p["endHour"]), int(p["endMinute"])
    k = float(p["trailStopMultiplier"])
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    fh = fl = trail = np.nan
    taken, dr = False, 0
    for i in range(m):
        if hr[i] == sh and mn[i] == sm and i > 1:
            fh, fl, taken, dr, trail = hv[i], lv[i], False, 0, np.nan
        dist = (fh - fl) * k
        if not np.isnan(fh) and cv[i] > fh and not taken and hr[i] > sh:
            le[i], trail, taken, dr = True, cv[i] - dist, True, 1
        if not np.isnan(fl) and cv[i] < fl and not taken and hr[i] > sh:
            se[i], trail, taken, dr = True, cv[i] + dist, True, -1
        if dr == 1 and not np.isnan(trail):
            trail = max(trail, cv[i] - dist)
            if cv[i] <= trail:
                lx[i] = True
        if dr == -1 and not np.isnan(trail):
            trail = min(trail, cv[i] + dist)
            if cv[i] >= trail:
                sx[i] = True
        if taken and hr[i] == eh and mn[i] == em:
            lx[i] = sx[i] = True
    idx_ = c.index
    S = lambda a: pd.Series(a, index=idx_)  # noqa: E731
    return S(le), S(lx & ~le), S(se), S(sx & ~se)


def portfolio_kwargs(**params):
    return {}
