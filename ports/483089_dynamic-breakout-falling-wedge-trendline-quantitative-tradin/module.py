"""Falling-wedge breakouts from the last two pivot highs and lows, long only, with a 2 % stop / 20 % target, daily
(broker-day) bars: when the last two pivot highs and lows both fall and the upper line falls faster than the lower,
a close crossing above the upper trendline goes long.
Port of FMZ strategy #483089 "动态突破下降楔形趋势线量化交易策略-Dynamic-Breakout-Falling-Wedge-Trendline-Quantitative-Trading-Strategy" (Falling Wedge Strategy by Nitin).

FMZ source id: 483089

Source
    https://www.fmz.com/strategy/483089 (PineScript v6, FMZ last modified 2025-02-27 17:02:08).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 111-169), pivots 5 / 5, TP 20 %, SL 2 %
    the two latest pivot highs (h1 newer, h2 older) and lows; upper = h2 + slope x (bar_index - i2) (lower alike)
    wedge = h1 < h2 and l1 < l2 and m_upper < m_lower < 0 (both negative)
    inside the wedge block: crossover(close, upper) -> entry + exit(stop = close x 0.98, limit = close x 1.20)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.pivothigh / pivotlow confirmed rightBars after the pivot (strict extremes, as #430850's _pivots).
    * ta.crossover is called only inside the wedge block, so its previous values are those of the last bar on which the
      block ran (Pine keeps a function's history per call), as written; the first call never crosses.
    * The bracket is placed with the entry from the signal close: 2 % / 20 % re-based on the fill (house rule). A later
      signal while held re-places it: mark trailing_stop_pending.
    * Long only; the source has no shorts. Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00
      America/New_York) stamped with their first minute (as #430984); stops on daily bars: coarse_bar_stop.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, pivot trendlines and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483089_falling_wedge_breakout_long"
FAMILY = "pivot_levels"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "pivot_bars": [5, 3],
    "tp_pct": [20.0, 10.0],
}
DEFAULT_PARAMS = {"pivot_bars": 5, "tp_pct": 20.0, "sl_pct": 2.0}


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
    n = int(p["pivot_bars"])
    ph, pl = _pivots(h, n, n, True), _pivots(lo, n, n, False)
    m = len(c)
    le = np.zeros(m, dtype=bool)
    highs, lows = [], []                       # newest first: (value, bar index)
    prev_c = prev_up = np.nan                  # crossover history of the last call
    for t in range(m):
        if ph[t]:
            highs = [(h[t - n], t - n)] + highs[:1]
        if pl[t]:
            lows = [(lo[t - n], t - n)] + lows[:1]
        if len(highs) >= 2 and len(lows) >= 2:
            (h1, i1), (h2, i2) = highs
            (l1, j1), (l2, j2) = lows
            mu = (h1 - h2) / (i1 - i2)
            ml = (l1 - l2) / (j1 - j2)
            if h1 < h2 and l1 < l2 and mu < ml and mu < 0 and ml < 0:
                up = h2 + mu * (t - i2)
                if c[t] > up and prev_c <= prev_up and t + 1 < m:
                    le[t] = True
                prev_c, prev_up = c[t], up
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
