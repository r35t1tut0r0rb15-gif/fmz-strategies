"""Pivot trend-line crosses from flat with a bar-direction filter and a 1 % / 2 % bracket, hourly bars: when the last
confirmed pivot (20 / 20) was a low, the close crossing above it on an up-close bar goes long when flat; when it was a
high, the close crossing below it on a down-close bar goes short; a cross back through the level closes the trade.
Port of FMZ strategy #489189 "TrendSync-Pro-SMC-多时间框架趋势跟随策略-TrendSync-Pro-SMC-Multi-Timeframe-Trend-Following-Strategy" (TrendSync Pro (SMC)).

FMZ source id: 489189

Source
    https://www.fmz.com/strategy/489189 (PineScript v6, FMZ last modified 2025-04-02 15:42:17).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 187-242), pivots 20 / 20, higher timeframe "60", SL 1 %, TP 2 %
    trend_value = the last pivot (high or low), direction up after a pivot low, down after a pivot high
    htf_up = security("60", close) > its previous value  (the chart is 1-hour: the bar's own close vs the previous)
    flat: long = crossover(close, trend_value) and htf_up and direction up -> entry + exit(stop 1 %, limit 2 %)
          short = crossunder(close, trend_value) and htf_down and direction down -> mirrored
    long held and crossunder(close, trend_value) -> close;  short held and crossover -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * pivothigh / pivotlow(20, 20): strictly above (below) the 20 bars on each side, known 20 bars later; on a bar with
      both, the pivot low (written last) sets the level and the direction. The crosses compare with the level's
      previous value.
    * The "60" security on the 1-hour chart is the bar's own close (complete at its close).
    * The bracket is placed once, on the signal bar: sl_stop 1 %, tp_stop 2 % of the fill (scalars, house rule).
    * Entries only from flat: simulate() follows the house bracket on bars (from the fill bar), as the desktop's
      flat-only bracket ports; the level crosses are close-checked exits. Opposite entries cannot occur.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; pivots confirmed after their right bars; bracket fixed at entry.
    2 generic: PASS, pivot levels and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489189_pivot_trendline_cross_flat_bracket"
FAMILY = "pivot_levels"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trend_period": [20, 10],
    "tp_pct": [2.0, 4.0],
}
DEFAULT_PARAMS = {"trend_period": 20, "sl_pct": 1.0, "tp_pct": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _pivot_at(x, t, n, high):
    j = t - n
    if j - n < 0:
        return False
    v = x[j]
    left, right = x[j - n:j], x[j + 1:t + 1]
    if np.isnan(v) or np.isnan(left).any() or np.isnan(right).any():
        return False
    return (v > left.max() and v > right.max()) if high else (v < left.min() and v < right.min())


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    n = int(p["trend_period"])
    s_, t_ = p["sl_pct"] / 100, p["tp_pct"] / 100
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    level, prev_level, up_dir = np.nan, np.nan, False
    pos, entry_i = 0, -1
    for i in range(m):
        prev_level = level
        if _pivot_at(h, i, n, True):
            level, up_dir = h[i - n], False
        if _pivot_at(lo, i, n, False):
            level, up_dir = lo[i - n], True
        if pos != 0 and 0 <= entry_i <= i:               # house bracket from the fill price
            e = o[entry_i]
            if pos == 1 and (lo[i] <= e * (1 - s_) or h[i] >= e * (1 + t_)):
                pos = 0
            elif pos == -1 and (h[i] >= e * (1 + s_) or lo[i] <= e * (1 - t_)):
                pos = 0
        if i == 0 or np.isnan(level) or np.isnan(prev_level):
            continue
        x_up = c[i] > level and c[i - 1] <= prev_level
        x_dn = c[i] < level and c[i - 1] >= prev_level
        start = pos
        if start == 0 and i + 1 < m:
            if x_up and c[i] > c[i - 1] and up_dir:
                le[i], pos, entry_i = True, 1, i + 1
            elif x_dn and c[i] < c[i - 1] and not up_dir:
                se[i], pos, entry_i = True, -1, i + 1
        if start == 1 and entry_i <= i and x_dn:
            lx[i], pos = True, 0
        if start == -1 and entry_i <= i and x_up:
            sx[i], pos = True, 0
    return le, lx, se, sx


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in _run(bars_df, p))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
