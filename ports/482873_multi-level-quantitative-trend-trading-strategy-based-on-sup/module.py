"""Support / resistance break-and-retest entries from 3 / 3 pivots, always in the market, daily (broker-day) bars:
after the latest pivot low is broken, a bar closing back at or above it with its low within 0.5 % of it goes long;
after the latest pivot high is broken, a bar closing at or below it with its high within 0.5 % goes short.
Port of FMZ strategy #482873 "基于支撑阻力位突破和回测的多级量化趋势交易策略-Multi-Level-Quantitative-Trend-Trading-Strategy-Based-on-Support-Resistance-Breakout-and-Retest" (SR Breakout & Retest Strategy (4hr)).

FMZ source id: 482873

Source
    https://www.fmz.com/strategy/482873 (PineScript v5, FMZ last modified 2025-02-20 16:00:35).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 114-165), pivots 3 / 3, tolerance 0.005
    a new pivot low becomes the support (flags reset); low < support -> broken; broken and not retested and
    close >= support and |low - support| <= support x 0.005 -> retested, entry long (resistance mirrored, short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pivots are strict extremes confirmed 3 bars later (as #430850's _pivots). The break and the retest can fall on
      one bar, as written. Each level gives at most one entry.
    * Entries reverse (REVERSAL INTENDED); no exits, no stops. "4hr" in the title is a label. Daily bars are broker
      days (17:00 America/New_York) stamped with their first minute (as #430984). FREQ = "1D" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, pivot levels and a percentage tolerance.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted in original_sizing.txt.
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

NAME = "fmz_482873_pivot_break_retest_reversal_1d"
FAMILY = "pivot_levels"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pivot_bars": [3, 5],
    "tolerance": [0.005, 0.01],
}
DEFAULT_PARAMS = {"pivot_bars": 3, "tolerance": 0.005}


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


def _pivots(x, lb, rb, high):
    m = len(x)
    out = np.zeros(m, dtype=bool)
    for t in range(lb + rb, m):
        j = t - rb
        v = x[j]
        if np.isnan(v):
            continue
        left, right = x[j - lb:j], x[j + 1:t + 1]
        if np.isnan(left).any() or np.isnan(right).any():
            continue
        out[t] = (v > left.max() and v > right.max()) if high else (v < left.min() and v < right.min())
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    n, tol = int(p["pivot_bars"]), float(p["tolerance"])
    pl, ph = _pivots(lo, n, n, False), _pivots(h, n, n, True)
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sup = res = np.nan
    s_brk = s_ret = r_brk = r_ret = False
    for i in range(m):
        if pl[i]:
            sup, s_brk, s_ret = lo[i - n], False, False
        if ph[i]:
            res, r_brk, r_ret = h[i - n], False, False
        if not np.isnan(sup):
            if not s_brk and lo[i] < sup:
                s_brk = True
            if s_brk and not s_ret and c[i] >= sup and abs(lo[i] - sup) <= sup * tol:
                s_ret, le[i] = True, True
        if not np.isnan(res):
            if not r_brk and h[i] > res:
                r_brk = True
            if r_brk and not r_ret and c[i] <= res and abs(h[i] - res) <= res * tol:
                r_ret, se[i] = True, True
    le &= ~se                                            # both on one bar: the later short entry wins
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
