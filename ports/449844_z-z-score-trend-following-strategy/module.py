"""Z-score of the close against its EMA 100 and 100-bar sd, daily bars: crossing over +1 goes long, crossing under -1 goes short; reversing.
Port of FMZ strategy #449844 "基于Z值的趋势跟踪策略-Z-Score-Trend-Following-Strategy" (Price Based Z-Trend - strategy [presentTrading]).

FMZ source id: 449844

Source
    https://www.fmz.com/strategy/449844 (PineScript v5, FMZ last modified 2024-04-29 17:03:15).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 126-188), EMA 100; sd 100; threshold 1; direction Both; 10 % of equity, commission 0.1 %, slippage 1
    z = (close - ema100) / sd100;  crossover(z, 1) -> entry Long, close Short;  crossunder(z, -1) -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each crossing closes the opposite side and enters, so the strategy reverses at the crossings
      (the long's close at -1 and the short's at +1 coincide with the opposite entries). Pine's stdev
      is the population deviation. REVERSAL INTENDED. The 10 % of equity size is sizing; commission and
      slippage are costs (not ported). FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Z-score threshold crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 10 % of equity size stored; commission and slippage are costs, not ported.
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

NAME = "fmz_449844_zscore_ema100_threshold_cross_reversal"
FAMILY = "momentum_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [100, 50],
    "threshold": [1.0, 1.5],
}
DEFAULT_PARAMS = {"length": 100, "threshold": 1.0}


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
    z = (c - c.ewm(span=n, adjust=False).mean()) / c.rolling(n).std(ddof=0)
    t = float(p["threshold"])
    le = (z > t) & (z.shift(1) <= t)
    se = (z < -t) & (z.shift(1) >= -t)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
