"""Parabolic SAR flips confirmed by the last 5-bar pivot's side and a 2-bar fractal confirmed on the same bar, closed
at the opposite SAR flip, hourly bars.
Port of FMZ strategy #482787 "多重技术指标趋势反转量化交易策略结合动态SAR参数优化系统-Multi-Technical-Indicator-Trend-Reversal-Quantitative-Trading-Strategy-with-Dynamic-SAR-Parameter-Optimization-System" (ZigZag + Fractals + SAR Crossover Strategy).

FMZ source id: 482787

Source
    https://www.fmz.com/strategy/482787 (PineScript v6, FMZ last modified 2025-02-20 11:03:59).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 106-149), pivots 5 / 5, fractals 2 / 2, sar(0.02, 0.2, 0.02)
    pivot high confirmed -> is_uptrend := false; pivot low confirmed -> is_uptrend := true
    long = crossunder(sar, close) and is_uptrend and a 2 / 2 pivot low confirmed on this bar -> entry long
    short = crossover(sar, close) and not is_uptrend and a 2 / 2 pivot high confirmed on this bar -> entry short
    crossover(sar, close) -> close long; crossunder(sar, close) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.sar(start 0.02, increment 0.2, maximum 0.02) as written: the acceleration is capped at 0.02, so the SAR
      runs with a constant 0.02 factor (#428699 formula). The conventional 0.2 maximum is a GRID variant.
    * The zig-zag deviation input is unused by the source. Pivots are strict on both sides (as #430850), confirmed
      depth bars later, so nothing reads the future.
    * Closes are written after the entries: they act on the position held at the bar's start and never undo an
      entry on that bar (#430850). State machine; exits emitted only on going flat.
    * Entries reverse (REVERSAL INTENDED). Signal module, no stops. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, the parabolic SAR and confirmed pivots.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity, quoted in original_sizing.txt.
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

NAME = "fmz_482787_sar_flip_pivot_side_fractal"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sar_max": [0.02, 0.2],
    "depth": [5, 10],
}
DEFAULT_PARAMS = {"depth": 5, "fractal": 2, "sar_start": 0.02, "sar_inc": 0.2, "sar_max": 0.02}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _sar_pine(bars, start, inc, maximum):
    """ta.sar as TradingView documents it (pine_sar): starts on bar 1, direction from close vs
    the previous close; value capped by the previous two bars' lows (highs)."""
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    out = np.full(m, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, m):
        first = False
        if i == 1:
            if c[1] > c[0]:
                below, max_min, result = True, h[1], lo[0]
            else:
                below, max_min, result = False, lo[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if below:
            if result > lo[i]:
                first, below = True, False
                result, max_min, acc = max(h[i], max_min), lo[i], start
        else:
            if result < h[i]:
                first, below = True, True
                result, max_min, acc = min(lo[i], max_min), h[i], start
        if not first:
            if below and h[i] > max_min:
                max_min, acc = h[i], min(acc + inc, maximum)
            elif (not below) and lo[i] < max_min:
                max_min, acc = lo[i], min(acc + inc, maximum)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return pd.Series(out, index=bars.index)


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
    h = bars_df["high"].to_numpy(dtype=float)
    lo = bars_df["low"].to_numpy(dtype=float)
    c = bars_df["close"]
    dp, fr = int(p["depth"]), int(p["fractal"])
    zh, zl = _pivots(h, dp, dp, True), _pivots(lo, dp, dp, False)
    fu, fd = _pivots(h, fr, fr, True), _pivots(lo, fr, fr, False)
    sar = _sar_pine(bars_df, p["sar_start"], p["sar_inc"], p["sar_max"])
    s_up = ((sar > c) & (sar.shift(1) <= c.shift(1))).to_numpy()     # crossover(sar, close)
    s_dn = ((sar < c) & (sar.shift(1) >= c.shift(1))).to_numpy()     # crossunder(sar, close)
    m = len(h)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    up = False                                                       # var bool is_uptrend = false
    pos = 0
    for i in range(m):
        if zh[i]:
            up = False
        if zl[i]:
            up = True
        start = pos
        if s_dn[i] and up and fd[i] and pos != 1:
            le[i], pos = True, 1
        if s_up[i] and not up and fu[i] and pos != -1:
            se[i], pos = True, -1
        if s_up[i] and start == 1 and pos == 1:
            lx[i], pos = True, 0
        if s_dn[i] and start == -1 and pos == -1:
            sx[i], pos = True, 0
    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx), pd.Series(se, index=idx),
            pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
