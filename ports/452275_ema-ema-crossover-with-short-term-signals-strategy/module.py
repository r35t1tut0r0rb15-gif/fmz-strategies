"""An EMA 30 channel of highs and lows, daily bars, long only: a close over the EMA 30 of highs buys, a close under the EMA 30 of lows sells.
Port of FMZ strategy #452275 "EMA均线交叉与短期信号策略-EMA-Crossover-with-Short-term-Signals-Strategy" (EMA Crossover with Short-term Signals).

FMZ source id: 452275

Source
    https://www.fmz.com/strategy/452275 (PineScript v5, FMZ last modified 2024-05-23 17:52:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 87-121), EMA 30 of high / of low; EMA 144 / 34 / 76 plotted only
    close > ema(high, 30) -> entry Buy;  close < ema(low, 30) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both tests are states: the entry repeats while the close stays over the upper line (ignored
      while long) and the close comes on the first close under the lower line; the two cannot meet on
      one bar. The EMAs 144 / 34 / 76 are only plotted. Long only. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA high / low channel states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_452275_ema30_high_low_channel_long"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [30, 20, 50],
}
DEFAULT_PARAMS = {"length": 30}


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
    n = int(p["length"])
    c = bars_df["close"]
    up = bars_df["high"].ewm(span=n, adjust=False).mean()
    dn = bars_df["low"].ewm(span=n, adjust=False).mean()
    false = pd.Series(False, index=bars_df.index)
    return c > up, c < dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
