"""Larry Connors-style dips above the SMA 200, daily bars, long only: the close above the SMA 200 but under the lowest of the previous seven closes, on a bar that is the 7-bar low, goes long; the close above
the highest of the previous seven closes closes.
Port of FMZ strategy #443125 "The Compound Breakout Strategy" (Larry Connors por RON).

FMZ source id: 443125

Source
    https://www.fmz.com/strategy/443125 (PineScript v4, FMZ last modified 2024-02-29 14:07:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 156-198), 7-bar low / high of close[1]; SMA 200; 100 % of equity; dates (testPeriod true)
    close > sma200 and close < lowest(close[1], 7) and low == lowest(low, 7) -> entry Buy;  close > highest(close[1], 7) or close > highest(high, 7) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The second exit test compares the close with the highest high including its own bar, which can
      never be exceeded, so the exit is the close over the previous seven closes' high. Long only. The
      100 % of equity size is sizing. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, short-term lows in an uptrend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443125_connors_7bar_low_above_sma200_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "value1": [7, 5],
    "value2": [7, 10],
}
DEFAULT_PARAMS = {"value1": 7, "value2": 7, "length_mma": 200}


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
    v1, v2 = int(p["value1"]), int(p["value2"])
    entry = c.shift(1).rolling(v1).min()
    ext = c.shift(1).rolling(v2).max()
    mma = c.rolling(int(p["length_mma"])).mean()
    le = (c > mma) & (c < entry) & (lo == lo.rolling(v1).min())
    lx = (c > ext) | (c > h.rolling(v2).max())
    false = pd.Series(False, index=c.index)
    return le & ~lx, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
