"""EMA 10 against the EMA 20, daily bars: the EMA 10 over the EMA 20 is long, under it is short; reversing on each change of side.
Port of FMZ strategy #452363 "SMC-EMA-Strategy-with-PL-Projections-SMC与EMA策略以及PL预测" (SMC & EMA Strategy with P&L Projections (SMC-EMA)).

FMZ source id: 452363

Source
    https://www.fmz.com/strategy/452363 (PineScript v5, FMZ last modified 2024-05-24 18:05:39).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 83-125), EMA 10 / 20; projected take profit / stop lines plotted only
    ema10 > ema20 -> entry Enter Long;  else ema10 < ema20 -> entry Enter Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both entries are states: the entry repeats every bar (ignored while held) and the position
      flips when the EMAs change order. The take-profit / stop projections and the risk-reward ratio
      are only plotted. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA trend state.
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

NAME = "fmz_452363_ema10_20_state_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 5],
    "slow": [20, 50],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 20}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    false = pd.Series(False, index=bars_df.index)
    return f > s, false, f < s, false.copy()


def portfolio_kwargs(**params):
    return {}
