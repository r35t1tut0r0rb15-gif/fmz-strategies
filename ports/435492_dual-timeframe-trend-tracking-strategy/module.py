"""Two EMA pairs on one chart, broker days, long only: with the EMA 20 over the EMA 50 ("daily trend"), the EMA 10 crossing over the
EMA 30 ("hourly" cross) goes long and the EMA 10 crossing under the EMA 30 closes the long.
Port of FMZ strategy #435492 "Dual Timeframe Trend Tracking Strategy" (Dual Time Frame Strategy).

FMZ source id: 435492

Source
    https://www.fmz.com/strategy/435492 (PineScript v5, FMZ last modified 2023-12-15 13:46:47).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 118-145), EMA 20 / 50 trend; EMA 10 / 30 cross; all on the chart's own close
    dailyUpTrend = ema(close, 20) > ema(close, 50);  hourlyBuy = crossover(ema(close, 10), ema(close, 30));  hourlySell = crossunder(ema(close, 10), ema(close, 30))
    dailyUpTrend and hourlyBuy -> entry long;  dailyUpTrend and hourlySell -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "daily" and "hourly" names are only labels: no request.security is used, all four
      averages are on the chart's own close (the backtest header chart is daily). The sell closes
      only while the trend condition holds, as written (a long can outlive the trend). Long only.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average trend and cross.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435492_ema_trend_and_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len_short_h": [10, 5],
    "len_long_h": [30, 20],
}
DEFAULT_PARAMS = {"len_short_d": 20, "len_long_d": 50, "len_short_h": 10, "len_long_h": 30}


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
    ed_s = c.ewm(span=int(p["len_short_d"]), adjust=False).mean()
    ed_l = c.ewm(span=int(p["len_long_d"]), adjust=False).mean()
    eh_s = c.ewm(span=int(p["len_short_h"]), adjust=False).mean()
    eh_l = c.ewm(span=int(p["len_long_h"]), adjust=False).mean()
    trend = ed_s > ed_l
    buy = (eh_s > eh_l) & (eh_s.shift(1) <= eh_l.shift(1))
    sell = (eh_s < eh_l) & (eh_s.shift(1) >= eh_l.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return (trend & buy).fillna(False).astype(bool), (trend & sell).fillna(False).astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
