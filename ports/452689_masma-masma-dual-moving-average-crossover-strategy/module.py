"""SMA 20 / 50 crossings, daily bars: the cross up goes long, the cross down goes short; reversing.
Port of FMZ strategy #452689 "MASMA双均线交叉策略-MASMA-Dual-Moving-Average-Crossover-Strategy" (Combined Strategy (MASMA dual moving average crossover)).

FMZ source id: 452689

Source
    https://www.fmz.com/strategy/452689 (PineScript v5, FMZ last modified 2024-05-28 10:53:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 87-120), SMA 20 / 50
    crossover(sma20, sma50) -> entry Buy;  crossunder(sma20, sma50) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * There is no exit: positions end at the opposite entry. The labels are drawing only. REVERSAL
      INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (spot pair in the header only (the source sends shorts as written)).
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

NAME = "fmz_452689_sma20_50_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [20, 10],
    "long_len": [50, 100],
}
DEFAULT_PARAMS = {"short_len": 20, "long_len": 50}


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
    s = c.rolling(int(p["short_len"])).mean()
    l_ = c.rolling(int(p["long_len"])).mean()
    le = (s > l_) & (s.shift(1) <= l_.shift(1))
    se = (s < l_) & (s.shift(1) >= l_.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
