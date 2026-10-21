"""Close against the 14-bar linear regression intercept, 1-hour bars: a close above the intercept (the regression line's value at the window's newest bar, x = 0) is long, below is short, equal holds; an optional
switch trades the reverse; entries are sent on every bar of the state, reversing.
Port of FMZ strategy #436997 "Quant Strategy Based on Linear Regression Intercept" (Line Regression Intercept Backtest).

FMZ source id: 436997

Source
    https://www.fmz.com/strategy/436997 (PineScript v2, FMZ last modified 2023-12-29 11:45:20).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 163-180), length 14, source close, reverse off
    xX = L (L - 1) / 2;  xDivisor = xX^2 - L^2 (L - 1)(2L - 1) / 6;  xXY = sum of i x close[i], i = 0 .. L - 1;  slope = (L xXY - xX sum(close, L)) / xDivisor;  LRI = (sum - slope xX) / L
    pos = 1 if close > LRI, -1 if close < LRI, else pos[1];  possig = -pos when reverse;  entry Long / Short on possig

Interpretation choices (Pine rules in SURVEY_README.md)
    * The intercept is computed exactly as the script's sums (i = 0 is the newest bar). The state is a
      level, so the entry is sent on every bar of the state; a same-side entry while in the position is
      ignored (pyramiding 0). REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close against a regression line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436997_linreg_intercept_side_state"
FAMILY = "trend_filter"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 28],
}
DEFAULT_PARAMS = {"length": 14, "reverse": False}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    xx = n * (n - 1) * 0.5
    div = xx * xx - n * n * (n - 1) * (2 * n - 1) / 6
    xy = sum(i * c.shift(i) for i in range(n))
    s = c.rolling(n).sum()
    slope = (n * xy - xx * s) / div
    lri = (s - slope * xx) / n
    cv, lv = c.to_numpy(dtype=float), lri.to_numpy(dtype=float)
    m = len(cv)
    pos = np.zeros(m)
    prev = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if cv[i] > lv[i]:
                prev = 1.0
            elif cv[i] < lv[i]:
                prev = -1.0
            pos[i] = prev
    sig = -pos if p["reverse"] else pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(sig == 1, index=ix), false, pd.Series(sig == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
