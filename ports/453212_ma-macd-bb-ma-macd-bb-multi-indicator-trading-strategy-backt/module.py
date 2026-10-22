"""Close crossings of the SMA 50 (the default 'MA' / 'Long' choice), daily bars, long only: the close crossing over the SMA 50 while flat buys, crossing under it sells.
Port of FMZ strategy #453212 "MA-MACD-BB多指标交易策略回测工具-MA-MACD-BB-Multi-Indicator-Trading-Strategy-Backtesting-Tool" (MA MACD BB Backtester).

FMZ source id: 453212

Source
    https://www.fmz.com/strategy/453212 (PineScript v5, FMZ last modified 2024-06-03 09:49:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 107-232), indicator 'MA', side 'Long' (defaults); SMA 50; MACD 12 / 26 / 9 and Bollinger 20 / 2 unused; 100 % of equity by floor(equity / close)
    flat and crossover(close, sma50) -> entry Buy MA (qty floor(equity x 100 % / close));  crossunder(close, sma50) -> close Buy MA

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the default inputs only the MA branch on the long side trades; the MACD and Bollinger
      branches and the short side are other input choices, not ported. A cross over can only come
      while flat (the cross under before it has closed the trade). Long only. The quantity is sizing
      (stored). FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close / SMA 50 crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity-based quantity stored.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453212_close_sma50_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_length": [50, 20, 100],
}
DEFAULT_PARAMS = {"ma_length": 50}


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
    ma = c.rolling(int(p["ma_length"])).mean()
    c1, m1 = c.shift(1), ma.shift(1)
    le = (c > ma) & (c1 <= m1)
    lx = (c < ma) & (c1 >= m1)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
