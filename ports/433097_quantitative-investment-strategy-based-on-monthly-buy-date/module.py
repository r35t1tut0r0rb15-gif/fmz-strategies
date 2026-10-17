"""Day-of-month entry, 1-hour bars, long only: on the 26th of the month (exchange clock) a long opens. With the default
"close on exit day" off it is never closed (buy and hold from the first 26th); with it on, the long is closed on the
5th (exit day 6 minus one).
Port of FMZ strategy #433097 "Quantitative Investment Strategy Based on Monthly Buy Date" (Buy and Hold, which day of month is best to buy?).

FMZ source id: 433097

Source
    https://www.fmz.com/strategy/433097 (PineScript v4, FMZ last modified 2023-11-24 14:10:23).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 190-212), entry day 26, exit day 6, close on exit day false; date range always true
    dayofmonth(time) == 26 -> entry long;  dayofmonth(time) == 6 - 1 and useExitDay -> close_all
    not inDateRange and not useExitDay -> close_all (inDateRange is always true)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Clock (C6): dayofmonth uses the exchange time zone; on the header's BTC_USDT that is UTC. A bar
      belongs to the day of its open. Every bar of the 26th re-issues the entry (ignored while long).
    * The default (use_exit False) is one trade held to the end of the data, as written; use_exit True
      is the author's own option and is in the grid.
    * Long only; Opposite entries cannot occur. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; calendar-day entries and exits.
    2 generic: PASS, calendar days only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: calendar day of month in UTC (the header's exchange clock); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433097_day_of_month_long"
FAMILY = "calendar_seasonal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "entry_day": [26, 20],
    "use_exit": [False, True],
}
DEFAULT_PARAMS = {"entry_day": 26, "exit_day": 6, "use_exit": False, "tz": "UTC"}


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
    dom = np.asarray(bars_df.index.tz_convert(str(p["tz"])).day)
    ent = dom == int(p["entry_day"])
    ext = (dom == int(p["exit_day"]) - 1) & bool(p["use_exit"])
    m = len(dom)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if ent[i]:
            pos = 1
        if ext[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev == 0), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
