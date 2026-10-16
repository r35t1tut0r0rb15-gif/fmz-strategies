"""SMA 3 / SMA 50 cross, long only, broker days: SMA 3 crossing above SMA 50 goes long; SMA 3 crossing below SMA 40,
or the close crossing below SMA 50, closes the long.
Port of FMZ strategy #429470 "基于SMA指标的短中期趋势跟踪策略Short-Mid-Term-Trend-Following-Strategy-Based-on-SMA-Indicators" (MA Crossover).

FMZ source id: 429470

Source
    https://www.fmz.com/strategy/429470 (PineScript v4, FMZ last modified 2023-10-17 14:27:10).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 133-151), SMA 3 / 40 / 50
    crossover(sma3, sma50) -> entry long; crossunder(sma3, sma40) or crossunder(close, sma50) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 2009 start is a backtest window: dropped. The 10-unit quantity is sizing.
    * Long only. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crosses only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 10-unit quantity stored.
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

NAME = "fmz_429470_sma3_50_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [3, 5],
    "slow": [50, 30],
}
DEFAULT_PARAMS = {"fast": 3, "slow": 50, "exit_ma": 40}


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
    f, s, x = (c.rolling(int(p[k])).mean() for k in ("fast", "slow", "exit_ma"))
    xo = lambda a, b: (a > b) & (a.shift(1) <= b.shift(1))  # noqa: E731
    xu = lambda a, b: (a < b) & (a.shift(1) >= b.shift(1))  # noqa: E731
    long_e = xo(f, s).astype(bool)
    long_x = (xu(f, x) | xu(c, s)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
