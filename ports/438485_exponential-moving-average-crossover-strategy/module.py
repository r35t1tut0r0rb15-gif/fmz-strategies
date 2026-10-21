"""EMA 20 / 50 crossings on the side of the EMA 200, broker days: the EMA 20 crossing over the EMA 50 with both above the EMA 200 goes long, the cross under with both below goes short; reversing. The brackets
name entry ids that never trade, so they place no exit.
Port of FMZ strategy #438485 "Exponential Moving Average Crossover Strategy" (rt maax ema).

FMZ source id: 438485

Source
    https://www.fmz.com/strategy/438485 (PineScript v5, FMZ last modified 2024-01-12 14:04:37).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 103-144), EMA 20 / 50 / 200; cash quantity 100000, capital 100000, commission 0.27 %; date inputs unused
    crossover(ema 20, ema 50) and ema 20 > ema 200 and ema 50 > ema 200 -> entry "Long Entry", exit("exit", "long", stop = low x 0.97, limit = high x 1.12)
    crossunder and both under the EMA 200 -> entry "Short Entry", exit("exit", "short", stop = low x 0.97, limit = high x 1.5)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits name from_entry "long" / "short", but the entries are "Long Entry" / "Short Entry", so
      the exits attach to nothing and place no order, as written (owed: the matching ids). Positions end
      at the opposite entry. The date inputs feed no condition. strategy.entry reverses: REVERSAL
      INTENDED. The cash size, capital and commission are sizing / costs. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings and EMA 200 side.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the cash size, capital and commission stored.
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

NAME = "fmz_438485_ema20_50_cross_ema200_side"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "mid": [50, 100],
}
DEFAULT_PARAMS = {"fast": 20, "mid": 50, "slow": 200}


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
    md = c.ewm(span=int(p["mid"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    up = (f > md) & (f.shift(1) <= md.shift(1)) & (f > s) & (md > s)
    dn = (f < md) & (f.shift(1) >= md.shift(1)) & (md < s) & (f < s)
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
