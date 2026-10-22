"""SMA 9 / 21 crossings, daily bars, long only: a cross up goes long, a cross down closes; the 2 % / 10 % bracket re-sent from each bar's close is not ported.
Port of FMZ strategy #446963 "Dual Moving Average Crossover Strategy" (Moving Average Crossover Strategy (uugankhuu)).

FMZ source id: 446963

Source
    https://www.fmz.com/strategy/446963 (PineScript v5, FMZ last modified 2024-04-03 15:12:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-142), SMA 9 / 21; stop 2 %, target 10 % of the current close (every bar)
    crossover(sma9, sma21) -> entry Buy;  crossunder -> close Buy;  exit(Buy, stop = close x 0.98, limit = close x 1.1)  (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.exit is called on every bar with levels from that bar's close, so the stop and target
      move with the price after entry: not ported (mark trailing_stop_pending; as #438034). The SMA
      cross-down ends the trades meanwhile. Long only. No sizing code. FREQ = "1D" from the backtest
      header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket not ported (mark).
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the percent bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_446963_sma9_21_cross_long_moving_bracket_pending"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21}


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
    le = (f > s) & (f.shift(1) <= s.shift(1))
    lx = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
