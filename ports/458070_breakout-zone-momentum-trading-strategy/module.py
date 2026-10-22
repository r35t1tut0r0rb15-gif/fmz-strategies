"""Close crossings of the SMA 50 with a 20-bar range filter, daily bars: the close crossing over the SMA above the 20-bar low goes long, crossing under below the 20-bar high goes short; reversing.
Port of FMZ strategy #458070 "Breakout Zone Momentum Trading Strategy" (Breaker Blocks with Buy and Sell Signals).

FMZ source id: 458070

Source
    https://www.fmz.com/strategy/458070 (PineScript v5, FMZ last modified 2024-07-29 17:00:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 182-213), SMA 50 of close; lowest(low, 20) / highest(high, 20), the current bar included
    crossover(close, sma50) and close > lowest(low, 20) -> entry Long;  crossunder(close, sma50) and close < highest(high, 20) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The range filters include the current bar, as written, so they hold on almost every bar. There
      is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1D"
      from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with a range filter.
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

NAME = "fmz_458070_sma50_close_cross_range_filter_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [50, 20],
    "breaker": [20, 50],
}
DEFAULT_PARAMS = {"sma_len": 50, "breaker": 20}


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
    n = int(p["breaker"])
    sup, res = lo.rolling(n).min(), h.rolling(n).max()
    s = c.rolling(int(p["sma_len"])).mean()
    le = (c > s) & (c.shift(1) <= s.shift(1)) & (c > sup)
    se = (c < s) & (c.shift(1) >= s.shift(1)) & (c < res)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
