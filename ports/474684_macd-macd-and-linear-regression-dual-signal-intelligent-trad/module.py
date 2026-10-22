"""MACD crossings confirmed by a rising 24-bar regression slope, hourly bars, long only: a MACD 12 / 26 / 9 cross up while the regression slope is positive and rising buys; a cross down while the slope is negative and falling sells. The bracket re-sent every bar from that bar's close is not ported (pending).
Port of FMZ strategy #474684 "MACD与线性回归双重信号智能交易策略-MACD-and-Linear-Regression-Dual-Signal-Intelligent-Trading-Strategy" (SIMPLIFIED MACD & LRS Backtest by NHBProd).

FMZ source id: 474684

Source
    https://www.fmz.com/strategy/474684 (PineScript v6, FMZ last modified 2024-12-11 15:46:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-204), MACD 12 / 26 / 9 (EMA method); linear regression 24, "Rising Linear"; both used for entries and exits; target 10 %, stop 0.10 % of the current close (every bar)
    crossover(macd, signal) and slope > 0 and slope > slope[1] -> entry Buy;  every bar: exit(limit = close x 1.10, stop = close x 0.999);  crossunder(macd, signal) and slope < 0 and slope < slope[1] -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * slope = linreg(close, 24, 0) - linreg(close, 24, 1), the regression slope of the window. With
      both switches on, entries and exits need both tests (AND). The bracket is re-sent on every bar
      from that bar's close, so its levels move after entry: a level re-set every bar is not ported (as
      #438034, mark trailing_stop_pending). Long only. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crossings with a regression-slope filter; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_474684_macd_cross_rising_linreg24_slope_long_bracket_pending"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lr_length": [24, 48],
    "signal_len": [9, 5],
}
DEFAULT_PARAMS = {"lr_length": 24, "signal_len": 9}


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


def _slope(y, n):
    """Least-squares slope over the last n bars (linreg(y, n, 0) - linreg(y, n, 1))."""
    x = np.arange(n, dtype=float)
    xc = x - x.mean()
    sxx = (xc ** 2).sum()
    return y.rolling(n).apply(lambda v: np.dot(xc, v) / sxx, raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=int(p["signal_len"]), adjust=False).mean()
    sl = _slope(c, int(p["lr_length"]))
    le = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (sl > 0) & (sl > sl.shift(1))
    lx = (macd < sig) & (macd.shift(1) >= sig.shift(1)) & (sl < 0) & (sl < sl.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
