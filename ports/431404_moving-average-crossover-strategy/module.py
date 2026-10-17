"""SMA 5 against a triangular MA 10, broker days, long only: the SMA 5 crossing above the SMA 10 of the SMA 10 goes long;
crossing below closes the long.
Port of FMZ strategy #431404 "Moving Average Crossover Strategy" (MP Rollercoaster Strat).

FMZ source id: 431404

Source
    https://www.fmz.com/strategy/431404 (PineScript v3, FMZ last modified 2023-11-07 15:48:41).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 147-195), SMA 5, TRIMA 10 (sma of sma)
    trima = sma(sma(close, 10), 10);  crossover(sma(close, 5), trima) -> entry long;  crossunder -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * testPeriod() is always true. Long only; Opposite entries cannot occur. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431404_sma_trima_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 10],
    "n": [10, 20],
}
DEFAULT_PARAMS = {"fast": 5, "n": 10}


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
    n = int(p["n"])
    tri = c.rolling(n).mean().rolling(n).mean()
    s = c.rolling(int(p["fast"])).mean()
    up = ((s > tri) & (s.shift(1) <= tri.shift(1))).astype(bool)
    dn = ((s < tri) & (s.shift(1) >= tri.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
