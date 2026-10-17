"""SMA 9 / 21 crosses, reversing, with a 2 % stop and a 4 % target from the signal close, daily bars.
Port of FMZ strategy #482594 "混合型斐波那契动量均线交叉策略-Hybrid-Fibonacci-Momentum-MA-Crossover-Strategy" (Buy/Sell Strategy with TP, SL, Fibonacci Levels, and Trend).

FMZ source id: 482594

Source
    https://www.fmz.com/strategy/482594 (PineScript v5, FMZ last modified 2025-02-19 11:02:16).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 102-167), SMA 9 / 21, SL 2 %, TP 4 %
    crossover -> entry long with exit(stop = close x 0.98, limit = close x 1.04); crossunder -> short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Fibonacci levels and the trend label only feed drawings.
    * The bracket is placed with the entry: 2 % / 4 % of the signal close, re-based on the fill (house rule).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket set at entry.
    2 generic: PASS, two SMAs and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482594_sma9_21_cross_pct_bracket"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [2.0, 4.0],
    "tp_pct": [4.0, 8.0],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "sl_pct": 2.0, "tp_pct": 4.0}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
