"""SMA 50 / 200 golden / death crosses confirmed by the last pivot bar, daily bars: a golden cross with the close over the high of the last pivot-high confirmation bar goes long, a death cross under the low of the last pivot-low confirmation bar goes short; a death cross closes a long, a golden cross closes a short; reversing.
Port of FMZ strategy #474869 "Dynamic Pivot Points with Golden Cross Optimization System" (Pivot Points & Golden Crossover Strategy).

FMZ source id: 474869

Source
    https://www.fmz.com/strategy/474869 (PineScript v5, FMZ last modified 2024-12-12 16:12:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-136), SMA 50 / 200; pivot length 5; lookback 20 (unused)
    pivot_high = valuewhen(pivothigh(high, 5, 5), high, 0);  pivot_low mirror;  crossover(sma50, sma200) and close > pivot_high -> entry Long;  crossunder -> close Long;  crossunder and close < pivot_low -> entry Short;  crossover -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.valuewhen(pivothigh(...), high, 0) returns the high of the bar where the pivot is confirmed
      (5 bars after the pivot), not the pivot's own high, as written; kept in a loop (strict pivots).
      A close coinciding with the opposite entry only repeats the reversal (#437773), so it is masked on
      entry bars. The lookback input feeds nothing. REVERSAL INTENDED. No sizing code. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, golden / death crosses with pivot-bar filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474869_golden_death_cross_pivot_bar_filter_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_short": [50, 20],
    "length_long": [200, 100],
}
DEFAULT_PARAMS = {"length_short": 50, "length_long": 200, "pivot_length": 5}


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


def _pivot(x, side, span=5):
    """Strict pivot of x at t - span, confirmed at t (Pine ta.pivothigh / pivotlow on the chart bars)."""
    v = np.asarray(x, dtype=float)
    m = len(v)
    out = np.zeros(m, dtype=bool)
    for t in range(2 * span, m):
        c = v[t - span]
        rest = np.concatenate([v[t - 2 * span:t - span], v[t - span + 1:t + 1]])
        if np.isnan(c) or np.isnan(rest).any():
            continue
        out[t] = (c > rest).all() if side > 0 else (c < rest).all()
    return out


def _kept(level, hit):
    """The level of the last bar where `hit` held (na before the first), as a var."""
    v = np.asarray(level, dtype=float)
    out = np.full(len(v), np.nan)
    cur = np.nan
    for i in range(len(v)):
        if hit[i]:
            cur = v[i]
        out[i] = cur
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k = int(p["pivot_length"])
    ph = pd.Series(_kept(h, _pivot(h, 1, k)), index=c.index)
    pl = pd.Series(_kept(lo, _pivot(lo, -1, k)), index=c.index)
    a, b = c.rolling(int(p["length_short"])).mean(), c.rolling(int(p["length_long"])).mean()
    gc = (a > b) & (a.shift(1) <= b.shift(1))
    dc = (a < b) & (a.shift(1) >= b.shift(1))
    le = gc & (c > ph)
    se = dc & (c < pl)
    return le, dc & ~se, se, gc & ~le


def portfolio_kwargs(**params):
    return {}
