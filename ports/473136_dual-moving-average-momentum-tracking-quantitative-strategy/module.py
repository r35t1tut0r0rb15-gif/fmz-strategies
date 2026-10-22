"""Close crossings of a smoothed SMA 9 (SMA 5 of it), daily bars: the close crossing over the smoothing line goes long, crossing under goes short; reversing.
Port of FMZ strategy #473136 "Dual Moving Average Momentum Tracking Quantitative Strategy" (Moving Average 1.0 Strategy).

FMZ source id: 473136

Source
    https://www.fmz.com/strategy/473136 (PineScript v5, FMZ last modified 2024-11-27 15:06:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-135), SMA 9; smoothing SMA 5 of it (method SMA by default); offset 0
    crossover(close, smoothing) -> entry Buy;  crossunder(close, smoothing) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default smoothing method SMA is ported; the offset only shifts the plot. There is no exit:
      positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close crossings of a double-smoothed average.
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

NAME = "fmz_473136_close_cross_smoothed_sma9_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [9, 20],
    "smoothing": [5, 10],
}
DEFAULT_PARAMS = {"len": 9, "smoothing": 5}


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
    sm = c.rolling(int(p["len"])).mean().rolling(int(p["smoothing"])).mean()
    le = (c > sm) & (c.shift(1) <= sm.shift(1))
    se = (c < sm) & (c.shift(1) >= sm.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
