"""SMA 20 turning against its value 2 bars back, broker days: the SMA crossing over its own value 2 bars earlier goes long, crossing under goes short; reversing.
Port of FMZ strategy #438047 "Moving Average Cross Signal Strategy" (Moving averages-Strategy).

FMZ source id: 438047

Source
    https://www.fmz.com/strategy/438047 (PineScript v3, FMZ last modified 2024-01-08 15:54:32).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 123-184), current chart resolution; length 20, type 1 (SMA); colour smoothing 2; second MA off
    out1 = security(tickerid, chart period, sma(close, 20));  crossover(out1, out1[2]) -> entry long;  crossunder(out1, out1[2]) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * useCurrentRes is on, so the security() call returns the chart's own series. The MA type is swept
      over SMA and EMA (the VWMA option needs volume and is not swept). The second MA only plots.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average slope crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND427510 (3 members, best partner #427510, Jaccard 0.764); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438047_ma20_slope_cross"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atype": [1, 2],
    "len": [20, 50],
}
DEFAULT_PARAMS = {"atype": 1, "len": 20, "smoothe": 2}


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
    n = int(p["len"])
    out = c.ewm(span=n, adjust=False).mean() if int(p["atype"]) == 2 else c.rolling(n).mean()
    prev = out.shift(int(p["smoothe"]))
    up = (out > prev) & (out.shift(1) <= prev.shift(1))
    dn = (out < prev) & (out.shift(1) >= prev.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
