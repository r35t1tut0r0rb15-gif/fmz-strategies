"""SMA 14 / 28 crossings, broker days, long only: the fast SMA crossing over the slow one buys, crossing under closes the long.
Port of FMZ strategy #437748 "基于双MA叠加的自适应回测时间范围选择策略Adaptive-Backtest-Date-Range-Selection-Strategy-Based-on-Double-MA" (How To Auto Set Date Range).

FMZ source id: 437748

Source
    https://www.fmz.com/strategy/437748 (PineScript v4, FMZ last modified 2024-01-05 12:12:10).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 147-169), fast SMA 14, slow SMA 28; date range WEEKS 52 (window() = true)
    buy = crossover(sma 14, sma 28) -> entry L;  sell = crossunder(...) -> close L

Interpretation choices (Pine rules in SURVEY_README.md)
    * window() is true: the date-range inputs are dropped. Long only. No sizing code. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossing.
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

NAME = "fmz_437748_sma_14_28_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [14, 7],
    "slow": [28, 56],
}
DEFAULT_PARAMS = {"fast": 14, "slow": 28}


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
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
