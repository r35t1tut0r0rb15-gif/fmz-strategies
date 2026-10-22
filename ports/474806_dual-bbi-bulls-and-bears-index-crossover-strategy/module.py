"""Two Bull-and-Bear-Index crossings, daily bars, long only: the average of SMA 12 / 24 / 48 / 80 crossing over the average of SMA 120 / 240 / 480 / 600 buys, crossing under sells.
Port of FMZ strategy #474806 "Dual BBI Bulls and Bears Index Crossover Strategy" (BBI 多頭策略).

FMZ source id: 474806

Source
    https://www.fmz.com/strategy/474806 (PineScript v6, FMZ last modified 2024-12-12 11:16:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-137), BBI A: SMA 12 / 24 / 48 / 80; BBI B: SMA 120 / 240 / 480 / 600
    crossover(bbiA, bbiB) -> entry Long;  crossunder(bbiA, bbiB) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each BBI is the mean of its four SMAs. Long only. No sizing code. FREQ = "1D" from the backtest
      header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, BBI crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474806_bbi12_80_vs_bbi120_600_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "a_scale": [1.0, 0.5],
    "b_scale": [1.0, 0.5],
}
DEFAULT_PARAMS = {"a_scale": 1.0, "b_scale": 1.0}


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


def _bbi(c, lengths, scale):
    return sum(c.rolling(max(1, int(round(n * scale)))).mean() for n in lengths) / len(lengths)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a = _bbi(c, (12, 24, 48, 80), float(p["a_scale"]))
    b = _bbi(c, (120, 240, 480, 600), float(p["b_scale"]))
    le = (a > b) & (a.shift(1) <= b.shift(1))
    lx = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
