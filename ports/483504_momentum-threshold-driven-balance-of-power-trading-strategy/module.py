"""Balance of power crossing above 0.8 bought, crossing below -0.8 closed, daily (broker-day) bars, long only:
(close - open) / (high - low) crossing above 0.8 goes long; crossing below -0.8 closes it.
Port of FMZ strategy #483504 "动量阈值驱动的平衡力量交易策略-Momentum-Threshold-Driven-Balance-of-Power-Trading-Strategy" (Balance of Power for US30 4H).

FMZ source id: 483504

Source
    https://www.fmz.com/strategy/483504 (PineScript v5, FMZ last modified 2025-02-27 16:50:22).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 95-104), thresholds 0.8 / -0.8
    p = (close - open) / (high - low); crossover(p, 0.8) -> entry long; crossunder(p, -0.8) -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * A bar with high == low has no balance of power (division by zero: na), as in Pine.
    * The leverage input and qty = equity x leverage / close are sizing: not ported. "US30 4H" in the title is a label;
      the backtest header says 1d: FREQ = "1D", broker days (17:00 America/New_York) stamped with their first minute
      (as #430984).
    * Long only; the source has no shorts. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a bar-shape ratio.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the leverage qty is quoted in original_sizing.txt and not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483504_balance_of_power_threshold_long"
FAMILY = "momentum"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "entry_level": [0.8, 0.6],
    "exit_level": [-0.8, -0.6],
}
DEFAULT_PARAMS = {"entry_level": 0.8, "exit_level": -0.8}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    rng = (h - lo).where(h != lo)
    bop = (c - o) / rng
    up, dn = p["entry_level"], p["exit_level"]
    long_e = ((bop > up) & (bop.shift(1) <= up)).astype(bool)
    long_x = ((bop < dn) & (bop.shift(1) >= dn)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
