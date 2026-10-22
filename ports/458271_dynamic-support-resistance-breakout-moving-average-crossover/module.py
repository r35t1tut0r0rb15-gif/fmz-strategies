"""SMA 9 / 21 crossings with a 9-bar range filter, daily bars: the cross up with the close over the 9-bar low goes long, the cross down with the close under the 9-bar high goes short; reversing.
Port of FMZ strategy #458271 "Dynamic Support Resistance Breakout Moving Average Crossover Strategy" (Bank Nifty Intraday Strategy).

FMZ source id: 458271

Source
    https://www.fmz.com/strategy/458271 (PineScript v5, FMZ last modified 2024-07-31 14:33:44).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 164-211), SMA 9 / 21; lowest(low, 9) / highest(high, 9), the current bar included
    crossover(sma9, sma21) and close > support -> entry Buy Call;  crossunder and close < resistance -> entry Buy Put
    opentrades > 0: close Buy Call when sell;  opentrades < 0 (never): close Buy Put when buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.opentrades counts trades and is never negative, so the short's close never runs; the
      long's close comes with the short entry that reverses it (#437773). The range filters include the
      current bar, so they hold on almost every bar. The names (Bank Nifty, calls and puts) are labels;
      the rules are generic. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with a range filter.
    3 crypto-exchange-only: no (exchange pair in the header only (Bank Nifty named in the title)).
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

NAME = "fmz_458271_sma9_21_cross_range_filter_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [9, 5],
    "long_len": [21, 50],
}
DEFAULT_PARAMS = {"short_len": 9, "long_len": 21}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["short_len"])
    a, b = c.rolling(n).mean(), c.rolling(int(p["long_len"])).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (c > lo.rolling(n).min())
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (c < h.rolling(n).max())
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
