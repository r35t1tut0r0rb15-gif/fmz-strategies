"""Guppy average crossings, daily bars: the mean of EMA 3 / 5 / 8 / 10 / 12 / 15 crossing over the mean of EMA 30 / 35 / 40 / 45 / 50 / 60 goes long, crossing under goes short; reversing. The 10 % / 5 % bracket re-sent every bar from that bar's close is not ported (pending).
Port of FMZ strategy #474843 "Multi EMA Crossover Momentum Trend Following Strategy" (Pavan Guppy Strategy).

FMZ source id: 474843

Source
    https://www.fmz.com/strategy/474843 (PineScript v5, FMZ last modified 2024-12-12 14:46:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-141), short EMAs 3-15, long EMAs 30-60 (constants); target 10 %, stop 5 % of the current close (every bar); 10 % of equity
    crossover(shortAvg, longAvg) -> entry Buy;  crossunder -> entry Sell;  every bar: exit(Buy, limit = close x 1.10, stop = close x 0.95), exit(Sell, limit = close x 0.90, stop = close x 1.05)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are re-sent on every bar from that bar's close, so the levels move after entry: a
      level re-set every bar is not ported (as #438034, mark trailing_stop_pending). Positions end at
      the opposite entry until then. REVERSAL INTENDED. The equity share is not ported. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Guppy average crossings; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_474843_guppy_short_long_average_cross_reversal_bracket_pending"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    c = bars_df["close"]
    a = sum(c.ewm(span=n, adjust=False).mean() for n in (3, 5, 8, 10, 12, 15)) / 6.0
    b = sum(c.ewm(span=n, adjust=False).mean() for n in (30, 35, 40, 45, 50, 60)) / 6.0
    le = (a > b) & (a.shift(1) <= b.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
