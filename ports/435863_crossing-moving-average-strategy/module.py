"""Double EMA crossing, broker days: the EMA 5 crossing over the EMA 9 and the EMA 9 crossing over the EMA 21 on the same bar goes long; both
crossing under on the same bar goes short (reversing).
Port of FMZ strategy #435863 "Crossing Moving Average Strategy" (5/9/21 EMA Strategy with 200 and 100 EMA).

FMZ source id: 435863

Source
    https://www.fmz.com/strategy/435863 (PineScript v5, FMZ last modified 2023-12-19 13:34:30).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 143-164), EMA 5 / 9 / 21; EMA 100 and 200 are drawn only
    longCondition = crossover(ema5, ema9) and crossover(ema9, ema21);  shortCondition = crossunder(ema5, ema9) and crossunder(ema9, ema21);  entry long / short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both crossings must happen on the same bar, as written (a rare event). strategy.entry reverses:
      REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435863_ema_5_9_21_double_cross"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema5": [5, 3],
    "ema21": [21, 34],
}
DEFAULT_PARAMS = {"ema5": 5, "ema9": 9, "ema21": 21}


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
    a, b, d = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("ema5", "ema9", "ema21"))
    up = ((a > b) & (a.shift(1) <= b.shift(1))) & ((b > d) & (b.shift(1) <= d.shift(1)))
    dn = ((a < b) & (a.shift(1) >= b.shift(1))) & ((b < d) & (b.shift(1) >= d.shift(1)))
    false = pd.Series(False, index=bars_df.index)
    return up.fillna(False).astype(bool), false, dn.fillna(False).astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
