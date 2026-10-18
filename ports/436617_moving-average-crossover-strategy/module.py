"""SMA 10 / 40 crossings, broker days: the short SMA crossing over the long one goes long (closing a short); crossing under goes short (closing a long); the EMA 20 is only drawn.
Port of FMZ strategy #436617 "Moving Average Crossover Strategy" (MA Crossover Strategy).

FMZ source id: 436617

Source
    https://www.fmz.com/strategy/436617 (PineScript v5, FMZ last modified 2023-12-26 12:04:34).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 150-185), short 10, long 40, EMA 20
    buyCondition = crossover(sma10, sma40);  sellCondition = crossunder(sma10, sma40);  buy: entry Buy, close Sell;  sell: entry Sell (short), close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each crossing reverses the position (the close of the other side and the opposite entry arrive
      together). REVERSAL INTENDED. The default quantity is sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crossings.
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

NAME = "fmz_436617_sma_cross_reversal_daily"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [10, 20],
    "long_len": [40, 80],
}
DEFAULT_PARAMS = {"short_len": 10, "long_len": 40}


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
    s, l_ = c.rolling(int(p["short_len"])).mean(), c.rolling(int(p["long_len"])).mean()
    up = ((s > l_) & (s.shift(1) <= l_.shift(1))).fillna(False).astype(bool)
    dn = ((s < l_) & (s.shift(1) >= l_.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
