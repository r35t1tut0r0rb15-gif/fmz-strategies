"""The close and its 2-bar SMA crossing the 4-bar SMA on the same bar, broker days: both crossing up goes long, both crossing down goes short; reversing.
Port of FMZ strategy #482800 "Multiple Moving Average Crossover Trend Capture Strategy" (1/2/4 Moving Average STR 1.0.0).

FMZ source id: 482800

Source
    https://www.fmz.com/strategy/482800 (PineScript v6, FMZ last modified 2025-02-20 11:31:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-131), SMA 1 / 2 / 4
    crossover(sma1, sma4) and crossover(sma2, sma4) -> entry Long, close Short;  crossunder both -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SMA 1 is the close. Each signal closes the other side and enters, which is a reversal (the close
      does not act on the position being reversed, as #441963). REVERSAL INTENDED. No sizing code. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, short SMA crossings.
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

NAME = "fmz_482800_close_sma2_cross_sma4_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "t_length": [2, 3],
    "f_length": [4, 8],
}
DEFAULT_PARAMS = {"t_length": 2, "f_length": 4, "o_length": 1}


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
    a, b, f = (c.rolling(int(p[k])).mean() for k in ("o_length", "t_length", "f_length"))

    def xo(x, y):
        return (x > y) & (x.shift(1) <= y.shift(1))

    le = xo(a, f) & xo(b, f)
    se = xo(f, a) & xo(f, b)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
