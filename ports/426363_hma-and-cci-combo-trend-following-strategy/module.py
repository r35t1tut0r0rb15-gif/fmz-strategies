"""HMA + CCI: with the Hull MA rising, CCI(10) crossing above -50 goes long; with it falling, CCI
crossing under +50 goes short. A long is closed when CCI > 100, a short when CCI < -100.
Port of FMZ strategy #426363 "HMA and CCI Combo Trend Following Strategy".

Source
    https://www.fmz.com/strategy/426363 (PineScript v3, FMZ last modified 2023-09-11 15:02:37).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 69-136), hmaLen 21, cciLen 10, -50 / 50, -100 / 100
    hullma = wma(2 * wma(src, 21 / 2) - wma(src, 21), round(sqrt(21)))
    hullma[1] < hullma and crossover(cci, -50)  -> entry long
    hullma[1] > hullma and crossunder(cci, 50)  -> entry short
    position > 0 and cci > 100 -> close_all;  position < 0 and cci < -100 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * v3 integer division: 21 / 2 = 10. hmaExit is off (source default); the RCI functions and
      the leverage input do not reach the orders. The date window is a backtest window: dropped.
    * The exits test the position held at the bar close, and close_all fills after the bar's
      entry order, so a long whose bar also re-signals long but has CCI > 100 ends flat.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "3h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426363_hma_cci_trend"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-07, user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hma_len": [14, 21, 34],
    "cci_len": [10, 20],
}
DEFAULT_PARAMS = {"hma_len": 21, "cci_len": 10, "cci_lower": -50, "cci_upper": 50,
                  "cci_lower_exit": -100, "cci_upper_exit": 100}


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


def _cci(x, n):
    """ta.cci: (x - sma) / (0.015 * mean absolute deviation)."""
    ma = x.rolling(n).mean()
    mad = x.rolling(n).apply(lambda a: np.abs(a - a.mean()).mean(), raw=True)
    return (x - ma) / (0.015 * mad)


def _emit(target, index):
    """Signals from the position each bar's orders leave (1 / 0 / -1): a change to +-1 is an
    entry (reversing an opposite position), a change to 0 an exit of the side held."""
    m = len(target)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    prev = 0
    for i in range(m):
        n = target[i]
        if n != prev:
            if n == 1:
                le[i] = True
            elif n == -1:
                se[i] = True
            elif prev == 1:
                lx[i] = True
            else:
                sx[i] = True
        prev = n
    return tuple(pd.Series(x, index=index) for x in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["hma_len"])
    hull = _wma(2 * _wma(c, n // 2) - _wma(c, n), int(round(np.sqrt(n))))
    cci = _cci(c, int(p["cci_len"]))
    rising, falling = hull.shift(1) < hull, hull.shift(1) > hull
    c1 = cci.shift(1)
    long_ = (rising & (cci > p["cci_lower"]) & (c1 <= p["cci_lower"])).to_numpy()
    short = (falling & (cci < p["cci_upper"]) & (c1 >= p["cci_upper"])).to_numpy()
    xl = (cci > p["cci_upper_exit"]).to_numpy()
    xs = (cci < p["cci_lower_exit"]).to_numpy()
    target = np.zeros(len(c), dtype=int)
    pos = 0
    for i in range(len(c)):
        before = pos
        if long_[i]:
            pos = 1
        if short[i]:
            pos = -1
        if (before == 1 and xl[i]) or (before == -1 and xs[i]):
            pos = 0
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
