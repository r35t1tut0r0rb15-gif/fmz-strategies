"""Two-sd Bollinger (34) breakouts, daily bars: the close crossing over the upper band goes long, crossing under the lower band goes short; reversing (the first band block only plots).
Port of FMZ strategy #450857 "Bollinger-Bands-Stochastic-Oscillator-Strategy-布林带随机振荡器策略" (Unique Bollinger Bands Strategy).

FMZ source id: 450857

Source
    https://www.fmz.com/strategy/450857 (PineScript v5, FMZ last modified 2024-05-09 15:59:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-174), BB 34 / 2 (trades); a second 34 / 1 / 2 band set (plot only)
    crossover(close, upper) -> entry Long, close Short;  crossunder(close, lower) -> entry Short, close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each close comes with the opposite entry on the same bar: one reversal. Pine's stdev is the
      population deviation. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band breakouts.
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

NAME = "fmz_450857_bb34_two_sd_breakout_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [34, 20],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 34, "mult": 2.0}


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
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    upper = basis + float(p["mult"]) * sd
    lower = basis - float(p["mult"]) * sd
    c1 = c.shift(1)
    le = (c > upper) & (c1 <= upper.shift(1))
    se = (c < lower) & (c1 >= lower.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
