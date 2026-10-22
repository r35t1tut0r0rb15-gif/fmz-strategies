"""TEMA 9 / 26 crossings, daily bars: the cross up goes long, the cross down goes short; reversing.
Port of FMZ strategy #453234 "TEMA双均线交叉策略-TEMA-Dual-Moving-Average-Crossover-Strategy" (2 TEMA Cross Strategy).

FMZ source id: 453234

Source
    https://www.fmz.com/strategy/453234 (PineScript v5, FMZ last modified 2024-06-03 10:59:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-139), TEMA 9 / 26; capital 25000
    crossover(tema9, tema26) -> entry long;  crossunder -> close long;  crossunder -> entry short;  cross (either way) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * In call order a cross up enters long (reversing a short, whose close then finds it reversed) and
      a cross down closes the long and then enters the short (one reversal); the short's either-way
      close never meets a held short except on a cross up. REVERSAL INTENDED. The capital setting is
      sizing. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, TEMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital setting stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453234_tema9_26_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [9, 5],
    "len2": [26, 50],
}
DEFAULT_PARAMS = {"len1": 9, "len2": 26}


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


def _tema(x, n):
    e1 = x.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    e3 = e2.ewm(span=n, adjust=False).mean()
    return 3 * (e1 - e2) + e3


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    t1, t2 = _tema(c, int(p["len1"])), _tema(c, int(p["len2"]))
    le = (t1 > t2) & (t1.shift(1) <= t2.shift(1))
    se = (t1 < t2) & (t1.shift(1) >= t2.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
