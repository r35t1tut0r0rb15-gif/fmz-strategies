"""RSI trend (Zer3192): the orders follow the Hull MA 30 slope (versus two bars back): turning up goes
long, turning down goes short (always in); the RSI lines only draw.
Port of FMZ strategy #380525 "RSITrend".

Source
    https://www.fmz.com/strategy/380525 (PineScript v5, author Zer3192, FMZ last modified
    2022-08-29 19:57:44). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 44-81), Hull trend length 30
    hull = hma(close, 30);  buy = hull > hull[2];  sell = hull < hull[2]
    buy and sell[1] -> entry long; else sell and buy[1] -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.hma = wma(2 wma(x, n/2) - wma(x, n), round(sqrt(n))).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_380525_hull_slope_turn"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "trend_len": [20, 30, 55],
}
DEFAULT_PARAMS = {"trend_len": 30}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["trend_len"])
    hull = _wma(2 * _wma(c, n // 2) - _wma(c, n), int(round(np.sqrt(n))))
    buy = (hull > hull.shift(2)).to_numpy()
    sell = (hull < hull.shift(2)).to_numpy()
    lag = lambda a: np.concatenate([[False], a[:-1]])
    return _always_in(buy & lag(sell), sell & lag(buy), bars_df.index)


def portfolio_kwargs(**params):
    return {}
