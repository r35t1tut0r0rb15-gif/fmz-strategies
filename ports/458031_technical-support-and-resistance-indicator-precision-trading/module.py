"""20-bar range breakouts on the bar's colour, daily bars: a green bar closing over the previous 20-bar high goes long, a red bar closing under the previous 20-bar low goes short; reversing.
Port of FMZ strategy #458031 "Technical Support and Resistance Indicator Precision Trading Strategy" (Mars Signals: Precision Trading).

FMZ source id: 458031

Source
    https://www.fmz.com/strategy/458031 (PineScript v5, FMZ last modified 2024-07-29 13:39:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 196-229), highest / lowest 20 (previous bar); Bollinger 20 / 2 plotted only
    close > open and close > highest(high, 20)[1] -> entry Buy;  close < open and close < lowest(low, 20)[1] -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are those of the previous bar, so the current bar is not in its own comparison. There
      is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1D"
      from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, range breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458031_colour_confirmed_20bar_breakout_reversal"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 55, 10],
}
DEFAULT_PARAMS = {"length": 20}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    le = (c > o) & (c > h.rolling(n).max().shift(1))
    se = (c < o) & (c < lo.rolling(n).min().shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
