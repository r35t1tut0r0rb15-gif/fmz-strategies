"""Close / HMA 100 crossings, 1-hour bars: the close crossing over the Hull MA 100 goes long, crossing under goes short; reversing.
Port of FMZ strategy #440090 "Price Crossing Moving Average Trend Following Strategy" (Price X MA Cross).

FMZ source id: 440090

Source
    https://www.fmz.com/strategy/440090 (PineScript v4, FMZ last modified 2024-01-26 15:18:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-150), MA type HMA, length 100, source close; tolerance 0; short only off
    longCondition = crossover(close, ma x (1 + 0 %));  shortCondition = crossunder(close, ma x (1 - 0 %));  entry Short on short, entry Long on long

Interpretation choices (Pine rules in SURVEY_README.md)
    * With zero tolerance both bands are the HMA (length / 2 and rounded square root). strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close / HMA crossings.
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

NAME = "fmz_440090_close_hma100_cross"
FAMILY = "hull_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [100, 50],
    "tol": [0.0, 0.5],
}
DEFAULT_PARAMS = {"len": 100, "tol": 0.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _hma(src, n):
    return _wma(2 * _wma(src, n // 2) - _wma(src, n), int(round(np.sqrt(n))))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ma = _hma(c, int(p["len"]))
    t = float(p["tol"]) / 100
    ut, lt = ma * (1 + t), ma * (1 - t)
    up = (c > ut) & (c.shift(1) <= ut.shift(1))
    dn = (c < lt) & (c.shift(1) >= lt.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn & ~up, false.copy()


def portfolio_kwargs(**params):
    return {}
