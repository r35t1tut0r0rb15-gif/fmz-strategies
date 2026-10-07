"""MACD line / signal line cross, stop-and-reverse, on daily bars.
Port of FMZ strategy #356844 "MACD-pine".

Source
    https://www.fmz.com/strategy/356844 (PineScript, FMZ last modified 2022-05-23 18:08:17).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 35-47), fast 12, slow 26, signal 9
    [fast, slow, _] = ta.macd(close, 12, 26, 9)        (fast = MACD line, slow = signal line)
    fast > slow and fast[1] < slow[1] -> strategy.entry long
    else fast < slow and fast[1] > slow[1] -> strategy.entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine fills at the next open: the contract. strategy.entry reverses an open opposite
      position: REVERSAL INTENDED (portfolio_kwargs {}; the engine's default opposite-entry
      reversal applies). Always in after the first cross.
    * The cross uses strict `<`/`>` on the previous bar, as written (a touch is not a cross).
    * Daily bars (backtest period 1d) are broker days (17:00 New York).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_356844_macd_signal_cross_reverse"
FAMILY = "macd_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 12, 16],
    "slow": [21, 26, 34],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    warm = np.arange(len(c)) >= int(p["slow"])
    le = (macd > sig) & (macd.shift(1) < sig.shift(1)) & warm
    se = (macd < sig) & (macd.shift(1) > sig.shift(1)) & warm & ~le
    false = pd.Series(False, index=bars_df.index)
    return le.astype(bool), false.copy(), se.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
