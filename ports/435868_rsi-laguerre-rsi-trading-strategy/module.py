"""Laguerre filter momentum crossings, broker days: the sum of the filter's rising differences (cu) crossing over the sum of its falling
differences (cd) goes long; crossing under goes short (reversing).
Port of FMZ strategy #435868 "拉盖尔RSI交易策略Laguerre-RSI-Trading-Strategy" (Laguerre RSI).

FMZ source id: 435868

Source
    https://www.fmz.com/strategy/435868 (PineScript v3, FMZ last modified 2023-12-19 14:04:46).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 185-226), alpha 0.2; the filter starts from zero
    L0 = (1 - gamma) close + gamma L0[1] ... L3 (gamma = 1 - alpha);  cu = sum of positive (L0 - L1, L1 - L2, L2 - L3);  cd = sum of negative parts;  crossover(cu, cd) -> entry long;  crossunder(cu, cd) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The filter's previous values are zero before the first bar (nz), as written. The Laguerre RSI
      itself (cu / (cu + cd)) is only plotted; the orders cross cu and cd, which is the same as the RSI
      crossing 0.5. strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, filter momentum.
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

NAME = "fmz_435868_laguerre_cu_cd_cross"
FAMILY = "laguerre"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "alpha": [0.2, 0.4, 0.6],
}
DEFAULT_PARAMS = {"alpha": 0.2}


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
    cv = bars_df["close"].to_numpy(dtype=float)
    gamma = 1 - float(p["alpha"])
    m = len(cv)
    cu, cd = np.zeros(m), np.zeros(m)
    l0 = l1 = l2 = l3 = 0.0
    for i in range(m):
        p0, p1, p2 = l0, l1, l2
        l0 = (1 - gamma) * cv[i] + gamma * p0
        l1 = -gamma * l0 + p0 + gamma * l1
        l2 = -gamma * l1 + p1 + gamma * l2
        l3 = -gamma * l2 + p2 + gamma * l3
        cu[i] = (l0 - l1 if l0 > l1 else 0.0) + (l1 - l2 if l1 > l2 else 0.0) + (l2 - l3 if l2 > l3 else 0.0)
        cd[i] = (l1 - l0 if l0 < l1 else 0.0) + (l2 - l1 if l1 < l2 else 0.0) + (l3 - l2 if l2 < l3 else 0.0)
    u, d = pd.Series(cu, index=bars_df.index), pd.Series(cd, index=bars_df.index)
    le = ((u > d) & (u.shift(1) <= d.shift(1))).fillna(False).astype(bool)
    se = ((u < d) & (u.shift(1) >= d.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
