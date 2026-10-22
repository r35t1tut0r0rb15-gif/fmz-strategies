"""Super Guppy ribbons, daily bars, long only: the seven fast EMAs (3 to 21) and the fifteen slow EMAs (24 to 66) each stacked in order upward goes long; the fast ribbon losing its upward stack closes.
Port of FMZ strategy #442651 "Trend Following Strategy Based on Moving Average Combination" (CM Super Guppy ala WY).

FMZ source id: 442651

Source
    https://www.fmz.com/strategy/442651 (PineScript v3, FMZ last modified 2024-02-23 14:54:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 145-275), fast EMAs 3 / 6 / ... / 21; slow EMAs 24 / 27 / ... / 66; EMA 200 (plot only); pyramiding 1; 99 % of equity; dates (testPeriod true)
    colfastL = ema3 > ema6 > ... > ema21;  colslowL = ema24 > ema27 > ... > ema66;  enterLong = colfastL and colslowL -> entry WY Long;  exitLong = not colfastL -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The test period function returns true. The entry repeats while both ribbons stay stacked and is
      refused at pyramiding 1. Long only. The 99 % of equity size is sizing. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stacked EMA ribbons.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
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

NAME = "fmz_442651_super_guppy_ribbon_stack_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "step": [3, 2],
    "slow_start": [24, 30],
}
DEFAULT_PARAMS = {"step": 3, "slow_start": 24}


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


def _stacked(c, lens):
    e = [c.ewm(span=n, adjust=False).mean() for n in lens]
    ok = pd.Series(True, index=c.index)
    for a, b in zip(e[:-1], e[1:]):
        ok &= a > b
    return ok


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    st, s0 = int(p["step"]), int(p["slow_start"])
    fast = _stacked(c, [st * k for k in range(1, 8)])
    slow = _stacked(c, [s0 + st * k for k in range(15)])
    le = fast & slow
    lx = ~fast
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
