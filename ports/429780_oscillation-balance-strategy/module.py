"""Projected balance of power, long only by the source's zero-quantity short, broker days: the projected average of
BoP and its EMAs crossing above zero goes long; crossing below zero closes the long.
Port of FMZ strategy #429780 "Oscillation Balance Strategy" (Balance of Power).

FMZ source id: 429780

Source
    https://www.fmz.com/strategy/429780 (PineScript v4, FMZ last modified 2023-10-20 17:03:08).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 164-194), BoP EMAs 3 / 6 / 9 / 12 / 18
    BoP = (close - open) / (high - low); sumEMA = avg(BoP, ema3, ema6, ema9, ema12, ema18)
    projected = sumEMA + (sumEMA - sumEMA[2])
    crossover(projected, 0) -> entry long (qty 1); crossunder(projected, 0) -> entry short with qty 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short entry has quantity 0: read as "no short", so its only effect is to close the long
      (stated reading; Noro-style scripts use qty 0 to switch a side off). Long only.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle-body ratios only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed 1 / 0 quantities stored.
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

NAME = "fmz_429780_projected_balance_of_power"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "proj_lag": [2, 1],
    "slowest": [18, 30],
}
DEFAULT_PARAMS = {"proj_lag": 2, "slowest": 18}


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
    bop = (c - o) / (h - lo).replace(0.0, np.nan)
    e = lambda n: bop.ewm(span=int(n), adjust=False).mean()  # noqa: E731
    s = (bop + e(3) + e(6) + e(9) + e(12) + e(p["slowest"])) / 6
    k = int(p["proj_lag"])
    proj = s + (s - s.shift(k))
    long_e = ((proj > 0) & (proj.shift(1) <= 0)).astype(bool)
    long_x = ((proj < 0) & (proj.shift(1) >= 0)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
