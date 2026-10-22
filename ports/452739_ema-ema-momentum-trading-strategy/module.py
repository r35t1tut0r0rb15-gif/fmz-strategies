"""EMA 10 / 21 crossings acted on one bar late, daily bars: the bar after a cross up goes long, the bar after a cross down goes short; reversing.
Port of FMZ strategy #452739 "EMA动量交易策略-EMA-Momentum-Trading-Strategy" (EMA Crossover Strategy (one bar delayed)).

FMZ source id: 452739

Source
    https://www.fmz.com/strategy/452739 (PineScript v5, FMZ last modified 2024-05-28 17:28:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-124), EMA 10 / 21; signals delayed by one bar
    longCondition[1] -> entry Long;  shortCondition[1] -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries read the previous bar's crossing, so the order is sent one bar after the cross (and
      fills at the open after that). The valuewhen lines are unused. REVERSAL INTENDED. No sizing
      code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, delayed EMA crossings.
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

NAME = "fmz_452739_ema10_21_cross_one_bar_delay_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 5],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 21}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return up.shift(1, fill_value=False), false, dn.shift(1, fill_value=False), false.copy()


def portfolio_kwargs(**params):
    return {}
