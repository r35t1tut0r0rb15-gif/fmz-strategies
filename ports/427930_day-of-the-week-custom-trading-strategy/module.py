"""Day-of-week long, broker days: the position is long across a run of weekdays. As written, the entry
fires at the close of the first "Long" day and the close fires at the close of the first "None" day
after it; the source's day labels are one off (its "monday" setting acts on Pine dayofweek 1 = Sunday),
so the default set goes long at Sunday's close and flat at Wednesday's close.
Port of FMZ strategy #427930 "Day of the Week Custom Trading Strategy".

FMZ source id: 427930

Source
    https://www.fmz.com/strategy/427930 (PineScript v4, FMZ last modified 2023-09-26 20:49:44).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 182-222), settings sunday None, monday-wednesday Long, rest None
    timeframes = [7, 1, 2, 3, 4, 5, 6] (Pine dayofweek, 1 = Sunday) paired with the settings in order
    on a bar whose dayofweek matches entry i: if setting i != setting i-1 -> close_all, and if
    setting i is Long / Short -> entry
    => as written: Long on dayofweek 1, 2, 3 (Sunday, Monday, Tuesday), None on 4-7

Interpretation choices (Pine rules in SURVEY_README.md)
    * AS WRITTEN with the shifted labels: the long days are Pine dayofweek `start_day` ..
      `start_day + n_days - 1` (default 1-3).
    * A bar's weekday is its broker-day date (the session ending 17:00 New York). Generic reading
      (stated): the setting is compared with the PREVIOUS BAR's day, not the calendar day before, so
      instruments with no weekend bars still trade (on 24/7 data the two readings agree). On FX the
      default set then enters at Monday's close and exits at Wednesday's close.
    * The date window (from 2021-06-14) is dropped. Long only.
    * Daily bars are broker days, stamped with their first minute. FREQ = "1D" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders on the calendar.
    2 generic: PASS, weekdays only (generic reading stated above).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); the weekday is the broker-day date.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427930_day_of_week_long"
FAMILY = "calendar_effect"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "start_day": [1, 2],
    "n_days": [3, 2],
}
DEFAULT_PARAMS = {"start_day": 1, "n_days": 3}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    day = broker_day(bars_df.index)
    dow = (np.asarray(day.weekday) + 1) % 7 + 1          # pandas Mon=0 .. Sun=6 -> Pine Sun=1 .. Sat=7
    s, n = int(p["start_day"]), int(p["n_days"])
    long_days = {((s - 1 + k) % 7) + 1 for k in range(n)}
    setting = np.array([1 if d in long_days else 0 for d in dow], dtype=np.int8)
    m = len(setting)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(1, m):
        if setting[i] != setting[i - 1]:
            pos = 1 if setting[i] == 1 else 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
