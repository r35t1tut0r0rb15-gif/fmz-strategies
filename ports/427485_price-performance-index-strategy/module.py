"""HPotter performance index, broker days: the 14-day rate of change above 0 is long, below 0 is short
(always in the market after the first signal).
Port of FMZ strategy #427485 "Price Performance Index Strategy".

FMZ source id: 427485

Source
    https://www.fmz.com/strategy/427485 (PineScript v2, FMZ last modified 2023-09-21 16:19:31).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 191-205), period 14, reverse off
    kpi = 100 (close - close[14]) / close[14]; pos = kpi > 0 ? 1 : kpi < 0 ? -1 : pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a rate of change.
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

NAME = "fmz_427485_hpotter_performance_index"
FAMILY = "slope_momentum"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [14, 7, 28],
}
DEFAULT_PARAMS = {"period": 14}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    n = int({**DEFAULT_PARAMS, **params}["period"])
    c = bars_df["close"]
    kpi = ((c - c.shift(n)) * 100 / c.shift(n)).to_numpy()
    m = len(kpi)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if kpi[i] > 0:
            pos = 1
        elif kpi[i] < 0:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
