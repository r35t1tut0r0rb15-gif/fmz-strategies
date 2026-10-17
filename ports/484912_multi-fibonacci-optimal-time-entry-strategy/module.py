"""Crosses of the 0.705 retracement between the latest 20-bar swing high and low, always in, broker days: the close
crossing above the 0.705 level while above the 0.618 level goes long; crossing below it while below the 0.618 level
goes short; each entry reverses the other.
Port of FMZ strategy #484912 "多重斐波那契优化时间入场策略-Multi-Fibonacci-Optimal-Time-Entry-Strategy" (ICT OTE Strategy).

FMZ source id: 484912

Source
    https://www.fmz.com/strategy/484912 (PineScript v6, FMZ last modified 2025-03-05 09:45:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 191-232), swing length 20
    highest(high, 20) == high -> swingHigh = high;  lowest(low, 20) == low -> swingLow = low
    fib(level) = swingHigh - (swingHigh - swingLow) x level
    long = crossover(close, fib 0.705) and close > fib 0.618;  short = crossunder(close, fib 0.705) and close < fib 0.618

Interpretation choices (Pine rules in SURVEY_README.md)
    * The swing tests include the current bar, as written (the latest bar making a 20-bar extreme); the levels are na
      until both swings exist.
    * Entries reverse (REVERSAL INTENDED); no other exit.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, retracement levels of rolling extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_484912_ote_fib705_cross"
FAMILY = "fibonacci_retracement"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
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


def _latest(flag, value):
    """Value at the latest bar where flag was true (na before), as a var updated under an if."""
    out = np.full(len(value), np.nan)
    cur = np.nan
    for i in range(len(value)):
        if flag[i]:
            cur = value[i]
        out[i] = cur
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    sh = _latest((h.rolling(n).max() == h).to_numpy(), h.to_numpy(dtype=float))
    sl = _latest((lo.rolling(n).min() == lo).to_numpy(), lo.to_numpy(dtype=float))
    f705 = pd.Series(sh - (sh - sl) * 0.705, index=c.index)
    f618 = pd.Series(sh - (sh - sl) * 0.618, index=c.index)
    long_e = ((c > f705) & (c.shift(1) <= f705.shift(1)) & (c > f618)).astype(bool)
    short_e = ((c < f705) & (c.shift(1) >= f705.shift(1)) & (c < f618)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
