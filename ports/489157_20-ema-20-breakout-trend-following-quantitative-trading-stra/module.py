"""Close crossing EMA 20, long only, broker days: the close crossing above EMA 20 goes long; crossing below closes it.
Port of FMZ strategy #489157 "20均线趋势突破量化交易策略-EMA-20-Breakout-Trend-Following-Quantitative-Trading-Strategy" (EMA 20 Bullish Strategy).

FMZ source id: 489157

Source
    https://www.fmz.com/strategy/489157 (PineScript v6, FMZ last modified 2025-04-02 11:31:05).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 190-204), EMA 20
    crossover(close, ema20) -> entry long;  crossunder(close, ema20) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The win-rate counters only feed a label. Long only.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an EMA only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (2 trials), before any backtest.
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
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [20, 50],
}
DEFAULT_PARAMS = {"ema_len": 20}


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
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    up = ((c > e) & (c.shift(1) <= e.shift(1))).astype(bool)
    dn = ((c < e) & (c.shift(1) >= e.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
