"""MACD(12, 26, 9) crossings above zero over an SMA 20, daily bars, long only: the MACD crossing over its signal above zero with the close over the SMA 20 goes long; the close under the SMA 20 closes.
Port of FMZ strategy #444016 "MACD均线多头量化交易策略MACD-Moving-Average-Bullish-Quantitative-Trading-Strategy" (MACD Long Strategy).

FMZ source id: 444016

Source
    https://www.fmz.com/strategy/444016 (PineScript v5, FMZ last modified 2024-03-08 15:47:44).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 153-194), MACD 12 / 26 / 9; SMA 20
    crossover(macd, signal) and macd > 0 and close > sma20 -> entry Long;  close < sma20 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry price variable only records. Long only. No sizing code. FREQ = "1D" from the backtest
      header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crossings above zero with an SMA filter.
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

NAME = "fmz_444016_macd_cross_above_zero_sma20_long"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_length": [20, 50],
    "macd_fast": [12, 8],
}
DEFAULT_PARAMS = {"sma_length": 20, "macd_fast": 12, "macd_slow": 26, "macd_signal": 9}


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
    macd = c.ewm(span=int(p["macd_fast"]), adjust=False).mean() - c.ewm(span=int(p["macd_slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["macd_signal"]), adjust=False).mean()
    s = c.rolling(int(p["sma_length"])).mean()
    le = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (macd > 0) & (c > s)
    lx = c < s
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
