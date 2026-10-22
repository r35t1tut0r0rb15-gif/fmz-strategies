"""The 09:15 UTC 1-minute candle's range, once a day: from 10:00 a close over its high goes long, under its low goes short; a close back beyond the other side of the candle closes, and 15:30 closes everything.
Port of FMZ strategy #489035 "First Candle Breakout with Stop Loss or End of Day Closing Strategy" (First Candle Breakout - Close on SL or EOD).

FMZ source id: 489035

Source
    https://www.fmz.com/strategy/489035 (PineScript v5, FMZ last modified 2025-04-01 13:51:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 117-164), first candle 09:15; stop at the other side (close-tested); close-all 15:30
    09:15 -> first high / low := the bar's, taken := false, direction := 0
    hour > 9 and not taken and close > first high -> entry Buy, direction 1;  mirror -> entry Sell
    direction 1 and close <= first low -> close Buy;  direction -1 and close >= first high -> close Sell;  taken and 15:30 -> close all

Interpretation choices (Pine rules in SURVEY_README.md)
    * hour / minute on the Binance header read UTC, at each bar's opening time. The stops are tested on
      closes and sent as closes (exit signals, no stop module); the direction is kept after an exit, so
      later closes beyond the level close nothing, as written. One entry per day (reset at 09:15); a
      position opened late in the day can still be open when the next day's opposite entry comes, which
      reverses it (REVERSAL INTENDED). No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested stop and clock close.
    2 generic: PASS, first-candle range breakouts.
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

NAME = "fmz_489035_first_candle_0915_breakout_range_stop_1530_close"
FAMILY = "opening_range_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "startHour": [9, 13],
    "endHour": [15, 20],
}
DEFAULT_PARAMS = {"startHour": 9, "endHour": 15, "startMinute": 15, "endMinute": 30}


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
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    fh = fl = np.nan
    taken, dr = False, 0
    for i in range(m):
        if hr[i] == sh and mn[i] == sm and i > 1:
            fh, fl, taken, dr = hv[i], lv[i], False, 0
        if not np.isnan(fh) and cv[i] > fh and not taken and hr[i] > sh:
            le[i], taken, dr = True, True, 1
        if not np.isnan(fl) and cv[i] < fl and not taken and hr[i] > sh:
            se[i], taken, dr = True, True, -1
        if dr == 1 and cv[i] <= fl:
            lx[i] = True
        if dr == -1 and cv[i] >= fh:
            sx[i] = True
        if taken and hr[i] == eh and mn[i] == em:
            lx[i] = sx[i] = True
    idx_ = c.index
    S = lambda a: pd.Series(a, index=idx_)  # noqa: E731
    return S(le), S(lx & ~le), S(se), S(sx & ~se)


def portfolio_kwargs(**params):
    return {}
