"""October-to-January seasonal hold, long only, broker days: from flat, the first bar of October goes long; the first bar of January closes.
Port of FMZ strategy #439970 "Seasonal Reversal Intertemporal Trading Strategy" (Seasonality Benchmark).

FMZ source id: 439970

Source
    https://www.fmz.com/strategy/439970 (PineScript v4, FMZ last modified 2024-01-25 14:07:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-158), direction Long; entry month Oct, exit month Jan; 25 % of equity
    if opentrades == 0 and month == entry: entry Swing (long);  if opentrades > 0 and month == exit: close Swing

Interpretation choices (Pine rules in SURVEY_README.md)
    * month is read on the bar's UTC open (as #435514); a broker-day bar opens at 21:00 / 22:00 UTC the
      evening before, so the first bar counted in October is the first one opening in October. The
      entry and the close cannot share a bar. Long only. The 25 % of equity size and commission are
      sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ
      = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, calendar months.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); month on the UTC bar open.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439970_october_january_seasonal_long"
FAMILY = "calendar_seasonal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "entry_month": [10, 11],
    "exit_month": [1, 4],
}
DEFAULT_PARAMS = {"entry_month": 10, "exit_month": 1}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    mon = bars_df.index.tz_convert("UTC").month.to_numpy()
    em, xm = int(p["entry_month"]), int(p["exit_month"])
    m = len(mon)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and mon[i] == em:
            le[i], pos = True, 1
        elif pos == 1 and mon[i] == xm:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
