"""Parabolic SAR flips (start 0.02, increment 0.2, maximum 0.02 as written) with a 5 / 5 pivot trend flag and a 2 / 2 fractal on the same bar, hourly bars: SAR moving under the price in an up flag with a fresh fractal low goes long, SAR moving over the price in a down flag with a fresh fractal high goes short; the opposite flip closes; reversing.
Port of FMZ strategy #482787 "多重技术指标趋势反转量化交易策略结合动态SAR参数优化系统-Multi-Technical-Indicator-Trend-Reversal-Quantitative-Trading-Strategy-with-Dynamic-SAR-Parameter-Optimization-System" (ZigZag + Fractals + SAR Crossover Stratégiia).

FMZ source id: 482787

Source
    https://www.fmz.com/strategy/482787 (PineScript v6, FMZ last modified 2025-02-20 11:03:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-158), pivots 5 / 5 (trend flag); fractals 2 / 2; ta.sar(0.02, 0.2, 0.02); 10 % of equity
    pivothigh(5, 5) -> is_uptrend := false;  pivotlow(5, 5) -> is_uptrend := true
    crossunder(sar, close) and is_uptrend and pivotlow(2, 2) confirmed -> entry Long;  crossover(sar, close) and not is_uptrend and pivothigh(2, 2) -> entry Short
    crossover(sar, close) -> close Long;  crossunder(sar, close) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.sar takes (start, increment, maximum): the source passes 0.02, 0.2, 0.02, so the factor starts at
      0.02 and its cap is 0.02, a constant factor, as written. The pivots are strict on both sides (as
      #478737); a bar confirming both 5 / 5 pivots ends with the up flag (the low is set second). The
      entries come before the closes: an entry that reverses a position stands although the other side's
      close is true on that bar (as #441963). REVERSAL INTENDED. The 10 % of equity size is sizing.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SAR flips with pivot-trend and fractal filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_482787_sar_flip_pivot5_trend_fractal2_reversal"
FAMILY = "parabolic_sar"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "zigzag_depth": [5, 10],
    "sar_start": [0.02, 0.01],
}
DEFAULT_PARAMS = {"zigzag_depth": 5, "sar_start": 0.02, "sar_increment": 0.2, "sar_maximum": 0.02, "fractal_span": 2}


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


def _pivot(x, side, span=5):
    """Strict pivot of x at t - span, confirmed at t (Pine ta.pivothigh / pivotlow), on rolling
    windows: the centre beats every bar of the span on each side."""
    s = x if side > 0 else -x
    centre = s.shift(span)
    left = s.shift(span + 1).rolling(span).max()
    right = s.rolling(span).max()
    return ((centre > left) & (centre > right)).to_numpy()


def _sar(hv, lv, cv, start, inc, mx):
    """Pine's ta.sar as documented (pine_sar)."""
    m = len(cv)
    out = np.full(m, np.nan)
    res = mm = acc = np.nan
    below = None
    for i in range(1, m):
        first = False
        if i == 1:
            if cv[1] > cv[0]:
                below, mm, res = True, hv[1], lv[0]
            else:
                below, mm, res = False, lv[1], hv[0]
            first, acc = True, start
        res = res + acc * (mm - res)
        if below:
            if res > lv[i]:
                first, below = True, False
                res, mm, acc = max(hv[i], mm), lv[i], start
        else:
            if res < hv[i]:
                first, below = True, True
                res, mm, acc = min(lv[i], mm), hv[i], start
        if not first:
            if below:
                if hv[i] > mm:
                    mm, acc = hv[i], min(acc + inc, mx)
            else:
                if lv[i] < mm:
                    mm, acc = lv[i], min(acc + inc, mx)
        if below:
            res = min(res, lv[i - 1])
            if i > 1:
                res = min(res, lv[i - 2])
        else:
            res = max(res, hv[i - 1])
            if i > 1:
                res = max(res, hv[i - 2])
        out[i] = res
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    zd, fs = int(p["zigzag_depth"]), int(p["fractal_span"])
    zh, zl = _pivot(h, 1, zd), _pivot(lo, -1, zd)
    up_flag = np.zeros(len(zh), dtype=bool)
    flag = False
    for i in range(len(zh)):
        if zh[i]:
            flag = False
        if zl[i]:
            flag = True
        up_flag[i] = flag
    fr_up, fr_dn = _pivot(h, 1, fs), _pivot(lo, -1, fs)
    sar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                         float(p["sar_start"]), float(p["sar_increment"]), float(p["sar_maximum"])), index=c.index)
    x_up = ((sar > c) & (sar.shift(1) <= c.shift(1))).to_numpy()      # SAR moves over the price
    x_dn = ((sar < c) & (sar.shift(1) >= c.shift(1))).to_numpy()
    le = x_dn & up_flag & fr_dn
    se = x_up & ~up_flag & fr_up
    idx = c.index
    le, se = pd.Series(le, index=idx), pd.Series(se, index=idx)
    lx, sx = pd.Series(x_up, index=idx), pd.Series(x_dn, index=idx)
    return le, lx & ~se & ~le, se, sx & ~le & ~se


def portfolio_kwargs(**params):
    return {}
