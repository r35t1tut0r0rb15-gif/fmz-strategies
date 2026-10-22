"""Close crossing its SMA 50 outside the Bollinger bands, daily bars: the close crossing over the SMA while above the upper band (20, 2) goes long, crossing under while below the lower band goes short;
reversing.
Port of FMZ strategy #443039 "Simple Moving Average Trend Price Quantitative Strategy" (Trend, Momentum ve Volatilite Stratejisi).

FMZ source id: 443039

Source
    https://www.fmz.com/strategy/443039 (PineScript v4, FMZ last modified 2024-02-28 17:40:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 109-141), SMA 50; VWMA 14 (unused); BB 20 / 2
    crossover(close, sma50) and close > upperBB -> entry Buy, close Sell;  crossunder(close, sma50) and close < lowerBB -> entry Sell, close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The VWMA only names a momentum line and is unused. The closes repeat the reversals. Pine's stdev
      is the population deviation. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings beyond the bands.
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

NAME = "fmz_443039_sma50_cross_outside_band_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "trend_period": [50, 20],
    "bb_period": [20, 50],
}
DEFAULT_PARAMS = {"trend_period": 50, "bb_period": 20, "bb_dev": 2.0}


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
    t = c.rolling(int(p["trend_period"])).mean()
    n = int(p["bb_period"])
    mid = c.rolling(n).mean()
    dev = float(p["bb_dev"]) * c.rolling(n).std(ddof=0)
    le = (c > t) & (c.shift(1) <= t.shift(1)) & (c > mid + dev)
    se = (c < t) & (c.shift(1) >= t.shift(1)) & (c < mid - dev)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
