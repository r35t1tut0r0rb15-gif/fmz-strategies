"""Bollinger basis upcrossings with a take profit, broker days, long only: the close crossing over the SMA 20 buys; the trade carries a take profit that the script
writes as close x 1.005 TICKS, re-expressed as a fraction of the price.
Port of FMZ strategy #436136 "Bollinger Bands Based High Frequency Trading Strategy" (Estrategia Bollinger Bands).

FMZ source id: 436136

Source
    https://www.fmz.com/strategy/436136 (PineScript v5, FMZ last modified 2023-12-21 15:37:07).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 175-201), Bollinger 20 / 2; target "0.5 %"
    price_touches_basis_up = crossover(close, basis) -> entry "Operacion" (direction long as close > basis), qty 1;  exit(profit = close x (1 + 0.005))   (profit is in TICKS)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the upcross is traded (the direction test is always long). Criterion 2: the take profit is passed
      in TICKS (close x 1.005 ticks), a distance of 1.005 x close x mintick; the port reads it as a
      fraction of the price: 0.1 for a 0.1 tick (the literal reading), 0.005 as the author's stated 0.5 %.
      No stop exists. Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark
      coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target fixed at entry.
    2 generic: ADAPT, tick target -> fraction of the price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity and starting amount stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_436136_basis_upcross_long_target"
FAMILY = "bollinger_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [20, 30],
    "tp_frac": [0.1, 0.005],
}
DEFAULT_PARAMS = {"length": 20, "tp_frac": 0.1}


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
    basis = c.rolling(int(p["length"])).mean()
    le = ((c > basis) & (c.shift(1) <= basis.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp_frac"])}


def portfolio_kwargs(**params):
    return {}
