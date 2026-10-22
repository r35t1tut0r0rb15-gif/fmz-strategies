"""Close crossings of the EMA 20, broker days, long only: the cross up goes long, the cross down closes.
Port of FMZ strategy #489157 "20均线趋势突破量化交易策略-EMA-20-Breakout-Trend-Following-Quantitative-Trading-Strategy" (EMA 20 Bullish Strategy).

FMZ source id: 489157

Source
    https://www.fmz.com/strategy/489157 (PineScript v6, FMZ last modified 2025-04-02 11:31:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 181-227), EMA 20; 100 % of equity
    crossover(close, ema20) -> entry Long;  crossunder(close, ema20) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * A stray plot(close) sits before the strategy() line; the win-rate counters only label. Long only.
      MPL 2.0 source (the notice is kept: Mozilla Public License 2.0, © SirTraderUSA). Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close / EMA crossings.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489157_close_ema20_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "emaLength": [20, 10, 50],
}
DEFAULT_PARAMS = {"emaLength": 20}


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
    e = c.ewm(span=int(p["emaLength"]), adjust=False).mean()
    le = (c > e) & (c.shift(1) <= e.shift(1))
    lx = (c < e) & (c.shift(1) >= e.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
