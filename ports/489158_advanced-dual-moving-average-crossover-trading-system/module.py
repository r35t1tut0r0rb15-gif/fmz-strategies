"""SMA 5 / 21 crossings, 3-day bars, long only: the up-cross goes long, the down-cross closes (the per-bar 1 % / 2 % bracket is pending).
Port of FMZ strategy #489158 "Advanced Dual Moving Average Crossover Trading System" (Intraday MA Crossover Strategy).

FMZ source id: 489158

Source
    https://www.fmz.com/strategy/489158 (PineScript v5, FMZ last modified 2025-04-02 11:35:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 207-263), SMA 5 / 21; SL 1 %, TP 2 % of the current close
    crossover(sma5, sma21) -> entry Buy;  crossunder -> close Buy;  every bar: exit(stop = close x 0.99, limit = close x 1.02)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.exit is sent on every bar from that bar's close, so the bracket follows the price: not
      ported, mark trailing_stop_pending (as the C170-C175 readings); the down-cross is the exit. Long only.
      No sizing code. Bars are blocks of three broker days (17:00 America/New_York) counted from 1970-01-01,
      stamped with their first minute. FREQ = "3D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent bracket pending.
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: three-broker-day blocks (17:00 America/New_York, DST by the zone).
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_489158_sma5_21_cross_long_3d"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3D"  # backtest header period: 3d (three broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "shortLength": [5, 9],
    "longLength": [21, 50],
}
DEFAULT_PARAMS = {"shortLength": 5, "longLength": 21, "days": 3}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = c.rolling(int(p["shortLength"])).mean(), c.rolling(int(p["longLength"])).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    lx = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
