"""Bollinger %B crossing 0.2 upward on the same bar as CMO 14 crossing 0 upward goes long; %B crossing 0.8 downward
with CMO crossing 0 downward goes short; always in the market, daily (broker-day) bars.
Port of FMZ strategy #483052 "基于动量与波动率的趋势突破交易策略-Momentum-and-Volatility-Based-Trend-Breakthrough-Trading-Strategy" (CMO + Bollinger Bands (%B) Strategy).

FMZ source id: 483052

Source
    https://www.fmz.com/strategy/483052 (PineScript v6, FMZ last modified 2025-02-27 17:09:24).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 120-165), BB 20 x 2, CMO 14
    long = crossover(%B, 0.2) and crossover(cmo, 0); short = crossunder(%B, 0.8) and crossunder(cmo, 0)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.cmo = 100 x (sum of up moves - sum of down moves) / (their total) over 14 bars; ta.stdev is the population
      standard deviation.
    * Entries reverse (REVERSAL INTENDED); no exits, no stops. Daily bars are broker days (17:00 America/New_York)
      stamped with their first minute (as #430984). FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger %B and CMO.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
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

NAME = "fmz_483052_percent_b_cmo_joint_cross_1d"
FAMILY = "oscillator_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_mult": [2.0, 2.5],
    "cmo_len": [14, 9],
}
DEFAULT_PARAMS = {"bb_len": 20, "bb_mult": 2.0, "cmo_len": 14}


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
    n = int(p["bb_len"])
    basis, dev = c.rolling(n).mean(), p["bb_mult"] * c.rolling(n).std(ddof=0)
    pb = (c - (basis - dev)) / (2 * dev)
    d = c.diff()
    m = int(p["cmo_len"])
    su, sd = d.clip(lower=0).rolling(m).sum(), (-d).clip(lower=0).rolling(m).sum()
    cmo = 100 * (su - sd) / (su + sd)
    long_e = ((pb > 0.2) & (pb.shift(1) <= 0.2) & (cmo > 0) & (cmo.shift(1) <= 0)).astype(bool)
    short_e = ((pb < 0.8) & (pb.shift(1) >= 0.8) & (cmo < 0) & (cmo.shift(1) >= 0)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
