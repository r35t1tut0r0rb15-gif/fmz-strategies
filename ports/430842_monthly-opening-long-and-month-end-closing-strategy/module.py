"""Monday-to-Friday holding, 1-hour bars, long only: any bar of a Monday broker day goes long, any bar of a Friday broker day
closes the long.
Port of FMZ strategy #430842 "Monthly Opening Long and Month end Closing Strategy" (Buurmans Tutorial).

FMZ source id: 430842

Source
    https://www.fmz.com/strategy/430842 (PineScript v4, FMZ last modified 2023-11-02 14:23:40).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 163-205), buy Monday, sell Friday, long only, stop off
    dayofweek == monday -> entry long;  dayofweek == friday and LongOnly -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The day of week is that of the broker day (the session ending 17:00 America/New_York, DST by
      the zone), a declared calendar in place of the chart's exchange time zone (skill section 5).
    * The 2020 start filter is the author's window: dropped. The $150 stop option is off (and in price
      units): not ported. Long only; Opposite entries cannot occur. FREQ = "1h" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a weekday calendar rule.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity per entry stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) gives the weekday; no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430842_monday_to_friday_long"
FAMILY = "calendar_seasonal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "entry_day": [0, 1],
    "exit_day": [4, 3],
}
DEFAULT_PARAMS = {"entry_day": 0, "exit_day": 4}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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
    wd = broker_day(bars_df.index).dayofweek
    long_e = pd.Series(wd == int(p["entry_day"]), index=bars_df.index)
    long_x = pd.Series(wd == int(p["exit_day"]), index=bars_df.index)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
