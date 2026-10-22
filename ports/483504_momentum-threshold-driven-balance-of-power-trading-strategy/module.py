"""Balance of Power crossings, broker days, long only: (close - open) / (high - low) crossing up through 0.8 goes long, crossing down through -0.8 closes.
Port of FMZ strategy #483504 "Momentum Threshold Driven Balance of Power Trading Strategy" (Balance of Power for US30 4H).

FMZ source id: 483504

Source
    https://www.fmz.com/strategy/483504 (PineScript v5, FMZ last modified 2025-02-27 16:50:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-139), BOP levels 0.8 / -0.8; leverage 5 (quantity); 100 % of equity; commission 0.01
    p = (close - open) / (high - low);  crossover(p, 0.8) -> entry L;  crossunder(p, -0.8) -> close L

Interpretation choices (Pine rules in SURVEY_README.md)
    * A bar with no range gives na (division by zero), which never crosses. The labels, boxes and lines
      are drawing only. Long only. The leveraged quantity and 100 % of equity are sizing; the commission
      is a cost (the house cost model applies). The title's 4H is not the header's bar size (1d). Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Balance of Power level crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: leverage-5 quantity and 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483504_balance_of_power_0_8_cross_long"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
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
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    rng = h - lo
    bop = (c - o) / rng.where(rng != 0)
    a, b = float(p["entry_level"]), float(p["exit_level"])
    le = (bop > a) & (bop.shift(1) <= a)
    lx = (bop < b) & (bop.shift(1) >= b)
    false = pd.Series(False, index=c.index)
    return le, lx & ~le, false, false.copy()


def portfolio_kwargs(**params):
    return {}
