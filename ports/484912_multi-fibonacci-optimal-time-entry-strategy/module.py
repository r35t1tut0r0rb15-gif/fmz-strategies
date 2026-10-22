"""Optimal-trade-entry Fibonacci levels of the latest 20-bar swing high and low, broker days: the close crossing up through the 70.5 % retracement while over the 61.8 % level goes long, crossing down through it while under the 61.8 % level goes short; reversing, no other exit.
Port of FMZ strategy #484912 "Multi Fibonacci Optimal Time Entry Strategy" (ICT OTE Strategy).

FMZ source id: 484912

Source
    https://www.fmz.com/strategy/484912 (PineScript v6, FMZ last modified 2025-03-05 09:45:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 187-236), swing length 20; levels 0.705 / 0.618; 1 % of equity
    highest(high, 20) == high -> swingHigh := high;  lowest(low, 20) == low -> swingLow := low  (var, kept)
    fib(x) = swingHigh - (swingHigh - swingLow) x;  crossover(close, fib 0.705) and close > fib 0.618 -> entry Long;  crossunder(close, fib 0.705) and close < fib 0.618 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The swing levels are the last bar that was the 20-bar extreme (including the bar), kept until the
      next. The other Fibonacci levels are drawing only. Entries only: each reverses the other side
      (REVERSAL INTENDED), no other exit. The 1 % of equity size is sizing. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, swing Fibonacci retracement crossings.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 1 % of equity stored, not ported.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_484912_swing20_fib705_618_cross_reversal"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50, 10],
}
DEFAULT_PARAMS = {"length": 20}


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


def _carry(v):
    """Keep the last non-na value (a Pine var level), written as a loop."""
    out = np.full(len(v), np.nan)
    last = np.nan
    for i in range(len(v)):
        if not np.isnan(v[i]):
            last = v[i]
        out[i] = last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    sh = pd.Series(_carry(h.where(h.rolling(n).max() == h).to_numpy(dtype=float)), index=c.index)
    sl = pd.Series(_carry(lo.where(lo.rolling(n).min() == lo).to_numpy(dtype=float)), index=c.index)
    f705 = sh - (sh - sl) * 0.705
    f618 = sh - (sh - sl) * 0.618
    le = (c > f705) & (c.shift(1) <= f705.shift(1)) & (c > f618)
    se = (c < f705) & (c.shift(1) >= f705.shift(1)) & (c < f618)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
