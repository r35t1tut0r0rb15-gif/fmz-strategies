"""Time-of-day long, 1-hour bars: with the default slot choices (00:00-02:00 long, every other half-hour "None"), the bar
opening at 00:00 starts a long and the bar opening at 02:00 closes it, every day.
Port of FMZ strategy #433009 "Timeframe Power Trading Strategy" (Timeframe Time of Day Buying and Selling Strategy).

FMZ source id: 433009

Source
    https://www.fmz.com/strategy/433009 (PineScript v4, FMZ last modified 2023-11-23 15:32:00).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 202-346), 48 half-hour slots; defaults Long for 0000-0200, None elsewhere; date window 2021-06-14 to 2100
    current_time = hhmm of the bar's open (exchange time zone);  slot i active when its option != None
    current_time == slot end and the option differs from the next slot's -> close_all
    current_time == slot start and the option differs from the previous slot's -> entry long / short as the option says

Interpretation choices (Pine rules in SURVEY_README.md)
    * Clock times (check 9 / C6): hour and minute are in the exchange time zone; on the header's
      BTC_USDT that is UTC (no DST). The grid also declares America/New_York (DST by the zone) for
      instruments whose session clock is New York. A bar is matched by the time of its open.
    * The default slots give one long block: entry on the bar opening at 00:00 and close-out on the bar
      opening at 02:00 (end of slot 0130-0200); on 1-hour bars both times exist. The close-out is an
      explicit exit signal (a time exit, not a time stop). The source's labels are shifted by one slot
      against the times they test; the tested times are used.
    * The date window (from 2021-06-14) is dropped (the data decide the span). Long only; Opposite
      entries cannot occur. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; clock-time entries and exits.
    2 generic: PASS, clock times only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entry at 00:00 and exit at 02:00 (exit_hour in the grid), in UTC (header) or America/New_York (grid), DST by the zone; no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433009_time_of_day_long"
FAMILY = "calendar_seasonal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tz": ["UTC", "America/New_York"],
    "exit_hour": [2, 3],
}
DEFAULT_PARAMS = {"tz": "UTC", "entry_hour": 0, "exit_hour": 2}


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
    loc = bars_df.index.tz_convert(str(p["tz"]))
    mins = loc.hour * 60 + loc.minute
    ent = np.asarray(mins == int(p["entry_hour"]) * 60)
    ext = np.asarray(mins == int(p["exit_hour"]) * 60)
    m = len(ent)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if ext[i]:
            pos = 0
        if ent[i]:
            pos = 1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev == 0), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
