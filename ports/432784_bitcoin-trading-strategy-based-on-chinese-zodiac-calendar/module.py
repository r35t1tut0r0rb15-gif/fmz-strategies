"""Calendar-year cycle, broker days: in years whose number modulo 12 is 0, 1, 4, 5, 8 or 9 the strategy is long, in years
2, 6 or 10 short, in years 3, 7 or 11 flat.
Port of FMZ strategy #432784 "Bitcoin Trading Strategy Based on Chinese Zodiac Calendar" (Chinese Zodiac Calendar Strategy (CZC Strategy)).

FMZ source id: 432784

Source
    https://www.fmz.com/strategy/432784 (PineScript v5, FMZ last modified 2023-11-21 14:50:26).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 127-159), year % 12
    year % 12 in (0, 1, 4, 5, 8, 9) -> entry long, close short;  in (2, 6, 10) -> entry short, close long;  in (3, 7, 11) -> close both

Interpretation choices (Pine rules in SURVEY_README.md)
    * A calendar rule (no price input). The year is the broker day's own year (the session ending
      17:00 America/New_York, labelled by its end date); Pine reads the bar's year in the exchange
      time zone, so the switch can differ by the one bar around New Year (stated).
    * The closes written after the entries do not undo a reversal. REVERSAL INTENDED. Daily bars
      are broker days, stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a calendar rule.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: calendar year of the broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432784_zodiac_year_cycle"
FAMILY = "calendar_seasonal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "year_offset": [0],
}
DEFAULT_PARAMS = {"year_offset": 0}


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
    yd = (broker_day(bars_df.index).year.to_numpy() + int(p["year_offset"])) % 12
    tgt = np.where(np.isin(yd, [0, 1, 4, 5, 8, 9]), 1, np.where(np.isin(yd, [2, 6, 10]), -1, 0)).astype(np.int8)
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
