"""Hull MA 60 / Hull MA 175 cross, 2-hour bars: the fast Hull crossing above the slow one goes long, crossing
below goes short.
Port of FMZ strategy #428969 "Double Hull Moving Average Crossover Trading Strategy" (Hull MA).

FMZ source id: 428969

Source
    https://www.fmz.com/strategy/428969 (PineScript v4, FMZ last modified 2023-10-11 14:49:54).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 171-197), Hull 60 and 175 on close
    hull(n) = wma(2 x wma(close, n/2) - wma(close, n), round(sqrt(n)))
    crossover(hull60, hull175) -> entry long; crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * n/2 of an integer length is taken as integer division (175/2 -> 87), as Pine passes a whole
      number of bars to wma; round(sqrt(175)) = 13.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crosses only.
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

NAME = "fmz_428969_hull_60_175_cross"
FAMILY = "hull_ma"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [60, 30],
    "alength": [175, 100],
}
DEFAULT_PARAMS = {"length": 60, "alength": 175}


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
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def _hull(x, n):
    return _wma(2 * _wma(x, max(n // 2, 1)) - _wma(x, n), int(round(np.sqrt(n))))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = _hull(c, int(p["length"])), _hull(c, int(p["alength"]))
    long_e = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
