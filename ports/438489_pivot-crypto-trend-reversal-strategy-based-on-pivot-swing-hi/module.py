"""Hourly swing levels: the close crossing under the last confirmed pivot low (10 / 10) while above the close 150 bars ago goes long, a close above the last pivot high closes it; the close crossing over the last pivot high while below the close 150 bars ago goes short, a close under the last pivot low covers it; reversing.
Port of FMZ strategy #438489 "基于PIVOT高低点的加密货币趋势反转策略CRYPTO-TREND-REVERSAL-STRATEGY-BASED-ON-PIVOT-SWING-HIGH-AND-LOW-POINTS" (Swing Hi Lo (nkrastins95)).

FMZ source id: 438489

Source
    https://www.fmz.com/strategy/438489 (PineScript v5, FMZ last modified 2024-01-12 14:13:36).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 135-197), pivot high 10 / 10; pivot low 10 / 10; chart timeframe; close[150] trend filter
    ph = security(tickerid, "", last non-na pivothigh(10, 10), lookahead_on);  pl = same for pivotlow
    crossunder(close, pl) and close > close[150] -> entry long;  close > ph -> close long;  crossover(close, ph) and close < close[150] -> entry Short;  close < pl -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The timeframe input is empty (the chart's), so security() returns the chart series itself and
      lookahead_on reads nothing ahead; the helper returns the value of the latest confirmed pivot
      (found 10 bars after it). Pivots are strict. A close acts only on a position the bar's entries
      leave unchanged. The VWAP feeds nothing: volume is not used. REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, counter-trend breaks of confirmed swing levels with a 150-bar trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438489_swing_pivot_counter_break_close150_filter_1h_reversal"
FAMILY = "support_resistance"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pivot_len": [10, 5],
    "trend_bars": [150, 75],
}
DEFAULT_PARAMS = {"pivot_len": 10, "trend_bars": 150}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _pivot_hit(x, side, left, right):
    """pivothigh / pivotlow(x, left, right) found on this bar (strict), and the pivot value x[right]."""
    s = x if side > 0 else -x
    centre = s.shift(right)
    lft = s.shift(right + 1).rolling(left).max()
    rgt = s.rolling(right).max()
    return ((centre > lft) & (centre > rgt)).to_numpy(), x.shift(right).to_numpy(dtype=float)


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["pivot_len"])
    hh, hv = _pivot_hit(h, 1, n, n)
    lh, lv = _pivot_hit(lo, -1, n, n)
    ph = _fixnan(pd.Series(np.where(hh, hv, np.nan), index=c.index))
    pl = _fixnan(pd.Series(np.where(lh, lv, np.nan), index=c.index))
    old = c.shift(int(p["trend_bars"]))
    lc = ((c < pl) & (c.shift(1) >= pl.shift(1)) & (c > old)).to_numpy()
    sc = ((c > ph) & (c.shift(1) <= ph.shift(1)) & (c < old)).to_numpy()
    ex = (c > ph).to_numpy()
    cov = (c < pl).to_numpy()
    m = len(lc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if lc[i] and pos != 1:
            le[i], pos = True, 1
        elif sc[i] and pos != -1:
            se[i], pos = True, -1
        elif pos == 1 and ex[i]:
            lx[i], pos = True, 0
        elif pos == -1 and cov[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
