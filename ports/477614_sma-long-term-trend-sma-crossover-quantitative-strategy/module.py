"""SMA 5 / 20 crossings, broker days, long only: the SMA 5 crossing over the SMA 20 buys, the SMA 20 crossing back over the SMA 5 closes.
Port of FMZ strategy #477614 "长期趋势SMA均线交叉量化策略-Long-term-Trend-SMA-Crossover-Quantitative-Strategy" (Long-Term Growing Stock Strategy).

FMZ source id: 477614

Source
    https://www.fmz.com/strategy/477614 (PineScript v6, FMZ last modified 2025-01-06 17:01:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 87-156), SMA 5 / 20 (SMA 10 / 60 / 120 computed, unused); date filter always true
    sma5[1] <= sma20[1] and sma5 > sma20 -> entry Long Entry;  crossover(sma20, sma5) -> close Long Entry

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long-term growth test (SMA 20 over SMA 60) is computed and not used. Long only. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings.
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

NAME = "fmz_477614_sma5_20_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 10],
    "slow": [20, 50],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 20}


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
    le = (f.shift(1) <= s.shift(1)) & (f > s)
    lx = (s > f) & (s.shift(1) <= f.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
