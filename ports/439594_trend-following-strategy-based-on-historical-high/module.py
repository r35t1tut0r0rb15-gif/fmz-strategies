"""Drawdowns from the running high, long only, broker days: a close more than 20 % under the highest high since the data start goes long; a close within 1 % of that high closes.
Port of FMZ strategy #439594 "Trend Following Strategy Based on Historical High" (All-time-high).

FMZ source id: 439594

Source
    https://www.fmz.com/strategy/439594 (PineScript v4, FMZ last modified 2024-01-22 08:59:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 193-230), line inputs and years back (unused); buy zone 0.8, sell zone 0.99 of the running high
    var highestHigh = 0;  if high > highestHigh: highestHigh := high;  close < 0.8 highestHigh -> entry Buy;  close > 0.99 highestHigh -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The running high is the expanding maximum of the highs from the first bar of the data (it ends at
      the current bar), as written; the "years back" input and the zone plots are unused. The two
      conditions cannot share a bar. Long only. The 100 % of equity size is sizing. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, fractions of the running high.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
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

NAME = "fmz_439594_running_high_drawdown_buy_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "buy_frac": [0.8, 0.9],
    "sell_frac": [0.99, 0.95],
}
DEFAULT_PARAMS = {"buy_frac": 0.8, "sell_frac": 0.99}


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
    hh = bars_df["high"].expanding().max().clip(lower=0)
    le = c < hh * float(p["buy_frac"])
    lx = c > hh * float(p["sell_frac"])
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
