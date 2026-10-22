"""SMA 14 / 28 crossings, daily bars: the cross up goes long, the cross down goes short; reversing (the rest of the script is an expected-value table).
Port of FMZ strategy #454362 "Trend Following Adaptive Expected Value Assessment Strategy Based on Crossover Moving Averages" (Expected Value Panel (SMA 14 / 28 template)).

FMZ source id: 454362

Source
    https://www.fmz.com/strategy/454362 (PineScript v5, FMZ last modified 2024-06-17 16:29:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 119-296), SMA 14 / 28; monthly / yearly expected-value panel (display only)
    crossover(sma14, sma28) -> entry My Long Entry Id;  crossunder -> entry My Short Entry Id

Interpretation choices (Pine rules in SURVEY_README.md)
    * The expected-value panel only reads the strategy's equity and closed trades to fill a table; it
      places no order. There is no exit: positions end at the opposite entry. REVERSAL INTENDED. No
      sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings.
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

NAME = "fmz_454362_sma14_28_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [14, 7],
    "slow": [28, 50],
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
    a = c.rolling(int(p["fast"])).mean()
    b = c.rolling(int(p["slow"])).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
