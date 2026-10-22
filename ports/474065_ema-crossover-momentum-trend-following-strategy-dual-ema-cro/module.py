"""EMA 9 / 20 crossings, daily bars: the cross up goes long, the cross down goes short; reversing.
Port of FMZ strategy #474065 "EMA Crossover Momentum Trend Following Strategy Dual EMA Crossover Momentum Trend Following Strategy" (EMA Crossover Strategy with Buttons).

FMZ source id: 474065

Source
    https://www.fmz.com/strategy/474065 (PineScript v5, FMZ last modified 2024-12-05 16:51:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-130), EMA 9 / 20
    change(longCondition) and longCondition -> entry Buy;  change(shortCondition) and shortCondition -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * A crossing holds for one bar, so its change test passes on every crossing bar: the entries are
      the crossings. There is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing
      code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_474065_ema9_20_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [9, 5],
    "long_len": [20, 50],
}
DEFAULT_PARAMS = {"short_len": 9, "long_len": 20}


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
    a = c.ewm(span=int(p["short_len"]), adjust=False).mean()
    b = c.ewm(span=int(p["long_len"]), adjust=False).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
