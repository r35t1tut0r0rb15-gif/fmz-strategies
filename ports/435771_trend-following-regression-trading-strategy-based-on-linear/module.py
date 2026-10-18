"""SMA crossings with a regression filter, 1-hour bars: the close crossing over its SMA 14 with the close over the regression value goes
long; crossing under it with the close under the regression value goes short (reversing). The stop / target exits compare the close with
levels derived from the same close and never fire (as written).
Port of FMZ strategy #435771 "Trend Following Regression Trading Strategy Based on Linear Regression and Moving Average" (Regression Trading Strategy).

FMZ source id: 435771

Source
    https://www.fmz.com/strategy/435771 (PineScript v4, FMZ last modified 2023-12-18 17:34:29).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 170-218), SMA 14; regression value over the last 14 bars; stop 2 %, take profit 2 %
    line = slope n + intercept of the least-squares fit of src[i] on i = 0 .. n-1;  long = crossover(close, sma) and close > line;  short = crossunder(close, sma) and close < line
    exit(when = crossover(close, close 0.98) or crossover(close, close 1.02))   (levels computed from the same close)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The fit regresses the value i bars back on i (i = 0 is the current bar) and the "line" is read
      at i = n, one step further back than the oldest sample (as written); it is a lagged level, not
      the usual end-of-line value. The exit tests crossover(close, close x 0.98) and crossover(close,
      close x 1.02): the first is never true (the close is always above 0.98 of itself and was before),
      the second is never true, so there is no exit (as written; the intended stop and target are owed).
      strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average cross and a regression level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent stop and target inputs stored.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435771_sma_cross_regression_filter"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [14, 30, 50],
}
DEFAULT_PARAMS = {"n": 14}


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


def _line(c, n):
    """Pine linear_regression(close, n): x = i bars back (0 = now); value = slope n + intercept."""
    i = np.arange(n, dtype=float)
    sx, sx2 = i.sum(), (i * i).sum()

    def f(a):                                  # a runs oldest .. newest; src[i] = a[n - 1 - i]
        y = a[::-1]
        sy, sxy = y.sum(), (i * y).sum()
        slope = (n * sxy - sx * sy) / (n * sx2 - sx * sx)
        intercept = (sy - slope * sx) / n
        return slope * n + intercept

    return c.rolling(n).apply(f, raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["n"])
    sma = c.rolling(n).mean()
    reg = _line(c, n)
    cross_up = (c > sma) & (c.shift(1) <= sma.shift(1))
    cross_dn = (c < sma) & (c.shift(1) >= sma.shift(1))
    le = (cross_up & (c > reg)).fillna(False).astype(bool)
    se = (cross_dn & (c < reg)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
