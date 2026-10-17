"""Previous-day pivot crosses on daily bars, long only, as written: from flat, a broker day that opens below the previous
day's pivot (H + L + C) / 3 and closes above it goes long, with a stop sized from the previous close in ticks (re-expressed
as 5 % of the fill). The intraday clock rules do nothing on daily bars.
Port of FMZ strategy #434581 "Intraday Pivot Points Trading Strategy" (ARR-Pivote-India-Stategy).

FMZ source id: 434581

Source
    https://www.fmz.com/strategy/434581 (PineScript v4, FMZ last modified 2023-12-07 16:43:17).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 132-250), trade level PP (default), long on, short off; max loss 0.5 (x previous close, in ticks); session 0915-1530; hour < 13 entries, close all at hour 15
    PP = (PDH + PDL + PDC) / 3 (security 'D', x[1], lookahead_on);  open < PP and close > PP and hour < 13 -> entry long (when position_size <= 0)
    exit(loss = PDC x 0.5 ticks);  hour == 15 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels carry [1], so lookahead_on reads the last completed day: the previous broker
      day's high / low / close (17:00 America/New_York).
    * On the daily header chart the bar's hour is its start hour, so "hour < 13" always holds and
      "hour == 15" never does: both are inert and dropped (the intended Indian-session intraday
      version is owed). Shorts are off by default.
    * Criterion 2: the loss is 0.5 x the previous close in ticks, i.e. about 0.5 x mintick of the
      price: 5 % with the header's BTC tick of 0.1 (sl_stop 0.05 of the fill). Only the stop exits.
      Long only; an entry while long is ignored. Stop module: portfolio_kwargs {} (driver D4). Stops
      on daily bars: mark coarse_bar_stop. Daily bars are broker days, stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: ADAPT, the tick-sized loss -> a fraction of the fill; pivot from the prior broker day.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity 1 stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the hour rules are inert on daily bars and dropped); broker day 17:00 America/New_York.
Long only. Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_434581_prev_day_pivot_cross_long"
FAMILY = "pivot_levels"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "level": ["PP", "R1"],
    "sl_pct": [0.05, 0.02],
}
DEFAULT_PARAMS = {"level": "PP", "sl_pct": 0.05}


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
    pdh, pdl, pdc = h.shift(1), lo.shift(1), c.shift(1)
    pp = (pdh + pdl + pdc) / 3
    lvl = {"PP": pp, "R1": 2 * pp - pdl, "S1": 2 * pp - pdh, "PDH": pdh, "PDL": pdl}[str(p["level"])]
    le = ((o < lvl) & (c > lvl)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"])}


def portfolio_kwargs(**params):
    return {}
