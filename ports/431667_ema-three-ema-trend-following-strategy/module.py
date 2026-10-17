"""Three rising EMAs of the typical price (QuantCT), broker days: all three EMAs (10 / 20 / 30 of hlc3) rising holds a long,
all three falling holds a short, anything else is flat.
Port of FMZ strategy #431667 "三EMA趋势追踪策略Three-EMA-Trend-Following-Strategy" (PMA Strategy Idea).

FMZ source id: 431667

Source
    https://www.fmz.com/strategy/431667 (PineScript v4, FMZ last modified 2023-11-10 11:45:30).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 175-218), EMA 10 / 20 / 30 of hlc3, long and short, stop off
    enter_long = rising(ema1, 1) and rising(ema2, 1) and rising(ema3, 1) -> entry long;  not enter_long -> close long
    enter_short = all falling -> entry short;  not enter_short -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop-loss option is off by default. A close does not undo a reversal on the same bar, so
      the position is +1 while all rise, -1 while all fall and flat otherwise. strategy.entry
      reverses: REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA slopes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the commission stored in original_sizing.txt.
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

NAME = "fmz_431667_three_rising_emas"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "e1": [10, 5],
    "e3": [30, 60],
}
DEFAULT_PARAMS = {"e1": 10, "e2": 20, "e3": 30}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    tp = (bars_df["high"] + bars_df["low"] + bars_df["close"]) / 3
    es = [tp.ewm(span=int(p[k]), adjust=False).mean() for k in ("e1", "e2", "e3")]
    up = np.logical_and.reduce([(e > e.shift(1)).to_numpy() for e in es])
    dn = np.logical_and.reduce([(e < e.shift(1)).to_numpy() for e in es])
    tgt = np.where(up, 1, np.where(dn, -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
