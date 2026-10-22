"""SMA 14 side against a 20-bar regression line, 1-hour bars, long only: the close above the SMA 14 but under the rolling trendline goes long; the close under the SMA but above the trendline closes.
Port of FMZ strategy #440986 "基于SMA和滚动趋势线的量化交易策略Quantitative-Trading-Strategy-Based-on-SMA-and-Rolling-Trendline" (SMA Strategy with Rolling Trendline).

FMZ source id: 440986

Source
    https://www.fmz.com/strategy/440986 (PineScript v4, FMZ last modified 2024-02-04 15:18:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 155-200), SMA 14; trendline window 20; start / end date inputs (unused)
    trendline: least squares of close[i] on i = 0 .. window-1 (i bars back), value = slope (window - 1) + intercept;  long = close > sma and close < trendline -> entry Long;  exit = close < sma and close > trendline -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trendline is the regression of the last 20 closes on their bars-back count i (i = 0 the current
      bar), evaluated as written at i = window - 1: the fitted value at the OLDEST bar of the window. The date
      inputs are never used (the block runs under if true). The conditions are levels; an entry while long
      does nothing. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA side and rolling regression value.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_440986_sma14_rolling_trendline_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_period": [14, 28],
    "window": [20, 40],
}
DEFAULT_PARAMS = {"sma_period": 14, "window": 20}


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


def _trendline(c, n):
    """Least squares of close[i] on i (bars back, i = 0 current) over n bars, valued at i = n - 1."""
    v = c.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.lib.stride_tricks.sliding_window_view(v, n)[:, ::-1]   # column i = close[i]
        x = np.arange(n, dtype=float)
        sx, sx2 = x.sum(), (x * x).sum()
        sy, sxy = w.sum(axis=1), w @ x
        slope = (n * sxy - sx * sy) / (n * sx2 - sx * sx)
        icpt = (sy - slope * sx) / n
        out[n - 1:] = slope * (n - 1) + icpt
    return pd.Series(out, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    sma = c.rolling(int(p["sma_period"])).mean()
    tl = _trendline(c, int(p["window"]))
    le = (c > sma) & (c < tl)
    lx = (c < sma) & (c > tl)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
