"""Bollinger 20 / 2 %B crossing 0.2 up together with CMO 14 crossing zero up goes long, %B crossing 0.8 down with CMO crossing zero down goes short, broker days; reversing, no other exit.
Port of FMZ strategy #483052 "Momentum and Volatility Based Trend Breakthrough Trading Strategy" (CMO + Bollinger Bands (%B) Strategy).

FMZ source id: 483052

Source
    https://www.fmz.com/strategy/483052 (PineScript v6, FMZ last modified 2025-02-27 17:09:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 116-169), Bollinger 20 x 2.0 (%B); CMO 14
    crossover(%B, 0.2) and crossover(cmo, 0) -> entry Long;  crossunder(%B, 0.8) and crossunder(cmo, 0) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries only: each reverses the other side (REVERSAL INTENDED), no other exit. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, %B and CMO crossings together.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483052_pctb_0_2_0_8_cmo14_zero_cross_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_length": [20, 40],
    "cmo_length": [14, 9],
}
DEFAULT_PARAMS = {"bb_length": 20, "cmo_length": 14, "bb_mult": 2.0}


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
    n = int(p["bb_length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    upper, lower = basis + float(p["bb_mult"]) * sd, basis - float(p["bb_mult"]) * sd
    w = upper - lower
    pb = (c - lower) / w.where(w != 0)
    mom = c.diff()
    k = int(p["cmo_length"])
    su, sdn = mom.clip(lower=0).rolling(k).sum(), (-mom).clip(lower=0).rolling(k).sum()
    tot = su + sdn
    cmo = 100 * (su - sdn) / tot.where(tot > 0)
    le = (pb > 0.2) & (pb.shift(1) <= 0.2) & (cmo > 0) & (cmo.shift(1) <= 0)
    se = (pb < 0.8) & (pb.shift(1) >= 0.8) & (cmo < 0) & (cmo.shift(1) >= 0)
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
