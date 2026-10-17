"""Month-day check against the SMA 200, broker days, long only: on a broker day dated the 30th, a close above the SMA 200
goes (or stays) long and a close below it closes the long; nothing happens on other days (and never in February).
Port of FMZ strategy #434710 "月末动量突破200日均线策略End-of-Month-Breakout-on-200-Day-Moving-Average-Strategy" (200DMA last DOM - ajh).

FMZ source id: 434710

Source
    https://www.fmz.com/strategy/434710 (PineScript v5, FMZ last modified 2023-12-08 16:02:08).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 117-144), SMA 200; signal on dayofmonth == 30; dates 2018-9999
    dayofmonth(time) == 30 and close > sma200 -> entry long;  dayofmonth(time) == 30 and close < sma200 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The day of month is that of the broker day (17:00 America/New_York; the session's date), as
      the bar's date on the header chart. The date window (2018 to 9999) is the author's: dropped.
      Long only; an entry while long is ignored. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price against an average on a calendar day.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: calendar day of the broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434710_day30_sma200_long"
FAMILY = "calendar_seasonal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "dom": [30, 28],
    "sma_len": [200, 100],
}
DEFAULT_PARAMS = {"dom": 30, "sma_len": 200}


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
    c = bars_df["close"]
    sma = c.rolling(int(p["sma_len"])).mean()
    on = pd.Series(broker_day(bars_df.index).day == int(p["dom"]), index=bars_df.index)
    le = (on & (c > sma)).astype(bool)
    lx = (on & (c < sma)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
