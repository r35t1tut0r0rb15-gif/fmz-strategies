"""A once-a-day EMA 10 / 50 check on the hourly bar opening at 09:00 UTC: the fast EMA above the slow goes long, below goes short; reversing.
Port of FMZ strategy #477524 "Dynamic Filtering EMA Cross Strategy for Daily Trend Analysis" (Daily EMA Comparison Strategy).

FMZ source id: 477524

Source
    https://www.fmz.com/strategy/477524 (PineScript v5, FMZ last modified 2025-01-06 11:16:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 83-143), EMA 10 / 50; check time 09:00 GMT (1-minute window)
    isCheckTime = time >= timestamp("GMT-0", y, m, d, 9, 0) and time < that + 1 minute;  isCheckTime and ema10 > ema50 -> entry Long;  isCheckTime and ema10 < ema50 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * On hourly bars the check window holds only the bar whose open time is 09:00 UTC, so a signal comes
      at most once a day, on that bar's close; a day without that bar has no check. The repeat entry on
      the held side is ignored. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, daily EMA comparison at a fixed UTC hour.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: one check a day on the 09:00 UTC bar (fixed UTC, no DST); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477524_daily_0900utc_ema10_50_side_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 20],
    "check_hour": [9, 14],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 50, "check_hour": 9}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    t = bars_df.index.tz_convert("UTC")
    chk = pd.Series((t.hour == int(p["check_hour"])) & (t.minute == 0), index=c.index)
    false = pd.Series(False, index=c.index)
    return chk & (f > s), false, chk & (f < s), false.copy()


def portfolio_kwargs(**params):
    return {}
