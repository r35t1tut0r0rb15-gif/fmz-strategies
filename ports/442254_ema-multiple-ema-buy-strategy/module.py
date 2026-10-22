"""Stacked EMA 5 / 10 / 20 / 50 / 100 / 200 trend, broker days, long only: the EMAs stacked in order with the close above the EMA 5 goes long; the close under the EMA 200 closes.
Port of FMZ strategy #442254 "基于多EMA买入策略Multiple-EMA-Buy-Strategy" (Multiple EMA Buy Strategy with Price Condition).

FMZ source id: 442254

Source
    https://www.fmz.com/strategy/442254 (PineScript v5, FMZ last modified 2024-02-20 15:38:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 155-182), EMA 5 / 10 / 20 / 50 / 100 / 200 (fixed)
    ema5 > ema10 > ema20 > ema50 > ema100 > ema200 and close > ema5 -> entry Buy;  close < ema200 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are levels; an entry while long does nothing. Long only. No sizing code. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stacked EMAs and the EMA 200 exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_442254_six_ema_stack_ema200_exit_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slowest": [200, 150],
}
DEFAULT_PARAMS = {"slowest": 200}


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
    es = [c.ewm(span=n, adjust=False).mean() for n in (5, 10, 20, 50, 100, int(p["slowest"]))]
    le = c > es[0]
    for a, b in zip(es[:-1], es[1:]):
        le &= a > b
    lx = c < es[-1]
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
