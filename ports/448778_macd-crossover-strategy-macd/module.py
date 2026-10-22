"""CDC action zones from EMA 12 / 26, daily bars, long only: the first bar of the bull zone (EMA 12 above EMA 26 and the close above EMA 12) goes long; the first bar of the bear zone closes.
Port of FMZ strategy #448778 "MACD-Crossover-Strategy-MACD-交叉策略" (Advance EMA Crossover Strategy (CDC Action Zone)).

FMZ source id: 448778

Source
    https://www.fmz.com/strategy/448778 (PineScript v5, FMZ last modified 2024-04-18 17:56:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 103-170), EMA 12 / 26 of the close (smoothing 1)
    BullZone = ema12 > ema26 and price > ema12;  BearZone = ema12 < ema26 and price < ema12;  BullZone and not BullZone[1] -> entry Buy;  BearZone and not BearZone[1] -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * A smoothing of 1 makes the price the close. The colour zones only paint bars. Long only. No sizing
      code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA action-zone transitions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_448778_cdc_action_zone_transition_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 9],
    "slow": [26, 21],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26}


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
    bull = (f > s) & (c > f)
    bear = (f < s) & (c < f)
    le = bull & ~bull.shift(1, fill_value=False)
    lx = bear & ~bear.shift(1, fill_value=False)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
