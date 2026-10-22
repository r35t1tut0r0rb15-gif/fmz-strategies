"""Regression-channel breakouts of the open, 1-hour bars: a least-squares line through the previous 100 closes projected to the current bar, with one standard deviation either side; the open crossing over the
upper line goes long, under the lower line short; the open crossing back through the middle closes; reversing.
Port of FMZ strategy #440096 "Adaptive Linear Regression Channel Strategy" (Stealthy 7 Linear Regression Channel Strategy).

FMZ source id: 440096

Source
    https://www.fmz.com/strategy/440096 (PineScript v2, FMZ last modified 2024-01-26 15:48:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 157-222), length 100; mult1 1, mult2 1; range mode off; source open
    m, b = least squares of close[1 .. 100] against x = 1 .. 100;  STDDEV = sqrt(mean((close[i] - (i m + b))^2));  upper = b + STDDEV, lower = b - STDDEV, middle = b
    crossover(open, upper) -> entry RGLONG else cancel;  crossunder(open, lower) -> entry RGSHORT else cancel;  crossover(open, middle) and short -> close_all;  crossunder(open, middle) and long -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The line uses the 100 closes before the current bar with x counting back from 1, so b is its value
      projected to the current bar. The cancel calls act on market entries that have already filled and
      do nothing. The final close_all acts on the position held at the bar close and the bar ends flat
      (as #430380). The open is known at the bar's start. strategy.entry reverses: REVERSAL INTENDED. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, regression channel of past closes.
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

NAME = "fmz_440096_stealthy7_regression_channel_open"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [100, 50],
    "mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 100, "mult": 1.0}


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


def _channel(c, n):
    """b and the residual sd of the least-squares line of close[1 .. n] on x = 1 .. n (x = 1 newest)."""
    y = c.shift(1)
    g = pd.Series(np.arange(len(y), dtype=float), index=y.index)
    sy = y.rolling(n).sum()
    sgy = (g * y).rolling(n).sum()
    syy = (y * y).rolling(n).sum()
    sxy = (g + 1) * sy - sgy                             # x = t + 1 - g inside the window ending at t
    sx = n * (n + 1) / 2.0
    sxx = n * (n + 1) * (2 * n + 1) / 6.0
    m = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    b = sy / n - m * sx / n
    rss = syy - 2 * m * sxy - 2 * b * sy + m * m * sxx + 2 * m * b * sx + n * b * b
    return b, np.sqrt((rss / n).clip(lower=0))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    b, sd = _channel(c, int(p["length"]))
    k = float(p["mult"])
    up, lo = b + k * sd, b - k * sd

    def xo(x, y):
        return ((x > y) & (x.shift(1) <= y.shift(1))).to_numpy()

    lc, sc = xo(o, up), xo(lo, o)
    xm_up, xm_dn = xo(o, b), xo(b, o)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if lc[i] and pos != 1:
            new = 1
        elif sc[i] and pos != -1:
            new = -1
        if (xm_up[i] and pos == -1) or (xm_dn[i] and pos == 1):
            new = 0
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
