"""Ichimoku leading-span crossings (9 / 26 / 52, read at the current bar, not displaced), broker days: span A crossing over span B goes long, crossing under goes short; reversing.
Port of FMZ strategy #476280 "Cloud Based Bollinger Bands Double Moving Average Quantitative Trend Strategy" (Ichimoku Cloud Strategy).

FMZ source id: 476280

Source
    https://www.fmz.com/strategy/476280 (PineScript v6, FMZ last modified 2024-12-27 15:54:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-143), conversion 9, base 26, span B 52; displacement 26 (plots only)
    donchian(n) = avg(lowest(n), highest(n));  lead1 = avg(donchian(9), donchian(26)), lead2 = donchian(52);  crossover(lead1, lead2) -> entry Long;  crossunder -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The crossings use the spans' current values; the displacement only shifts the plots. ta.lowest /
      ta.highest with one argument read the low and the high. REVERSAL INTENDED. No sizing code. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku span crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_476280_ichimoku_span_ab_cross_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conversion": [9, 20],
    "span_b": [52, 120],
}
DEFAULT_PARAMS = {"conversion": 9, "base": 26, "span_b": 52}


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
    h, lo = bars_df["high"], bars_df["low"]

    def don(n):
        return (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2

    a = (don(p["conversion"]) + don(p["base"])) / 2
    b = don(p["span_b"])
    le = (a > b) & (a.shift(1) <= b.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=h.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
