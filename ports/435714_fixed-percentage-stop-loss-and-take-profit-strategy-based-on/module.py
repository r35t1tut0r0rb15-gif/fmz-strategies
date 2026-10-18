"""EMA 5 / 32 crosses with a percent bracket, broker days: the EMA 5 crossing over the EMA 32 goes long, crossing under goes short
(reversing); each trade carries a 5 % stop and a 10 % target on the average price.
Port of FMZ strategy #435714 "Fixed Percentage Stop Loss and Take Profit Strategy Based on Moving Averages" (Fixed Percent Stop Loss & Take Profit %).

FMZ source id: 435714

Source
    https://www.fmz.com/strategy/435714 (PineScript v4, FMZ last modified 2023-12-18 11:30:39).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 180-204), EMA 5 / 32; stop 5 %, take profit 10 %
    long = crossover(ema5, ema32) -> entry long;  short = crossunder(ema5, ema32) -> entry short;  long position: exit(stop = avg (1 - 5 %), limit = avg (1 + 10 %));  short position: exit(stop = avg (1 + 5 %), limit = avg (1 - 10 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is a fraction of the fill price (sl_stop 0.05, tp_stop 0.10, scalars). The opposite
      cross reverses the position: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Stops on daily bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, average cross and a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_435714_ema_5_32_cross_percent_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_per": [0.05, 0.03],
    "take_per": [0.10, 0.06],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 32, "stop_per": 0.05, "take_per": 0.10}


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
    e1 = c.ewm(span=int(p["fast"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = ((e1 > e2) & (e1.shift(1) <= e2.shift(1))).fillna(False).astype(bool)
    se = ((e1 < e2) & (e1.shift(1) >= e2.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop_per"]), "tp_stop": float(p["take_per"])}


def portfolio_kwargs(**params):
    return {}
