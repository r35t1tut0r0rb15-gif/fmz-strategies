"""One-sd Bollinger band breakouts, broker days: the close crossing over the upper 1 sd band goes long (closing a short); crossing under the
lower 1 sd band goes short (closing a long).
Port of FMZ strategy #435767 "Bollinger Bands Dual Standard Deviation Trading Strategy" (Bollinger Bands).

FMZ source id: 435767

Source
    https://www.fmz.com/strategy/435767 (PineScript v5, FMZ last modified 2023-12-18 17:23:42).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 128-163), Bollinger 34, bands at 1 sd (trades) and 2 sd (drawn only)
    longCondition = crossover(close, sma(close, 34) + stdev);  shortCondition = crossunder(close, sma(close, 34) - stdev);  entry long / short;  close Buy on shortCondition;  close Sell on longCondition

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 2 sd band and the multiplier input only draw the outer fills; the orders use the 1 sd bands.
      The explicit closes coincide with the reversal. REVERSAL INTENDED. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger band crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435767_bollinger_1sd_breakout"
FAMILY = "bollinger_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [34, 20, 50],
}
DEFAULT_PARAMS = {"length": 34}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = c.rolling(n).std(ddof=0)
    up1, lo1 = basis + dev, basis - dev
    le = ((c > up1) & (c.shift(1) <= up1.shift(1))).fillna(False).astype(bool)
    se = ((c < lo1) & (c.shift(1) >= lo1.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
