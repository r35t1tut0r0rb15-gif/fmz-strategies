"""Hull Suite: HMA 55 above its value two bars ago goes long, below goes short (always in).
Port of FMZ strategy #365727 "Hull Suite Strategy".

Source
    https://www.fmz.com/strategy/365727 (PineScript v4, FMZ last modified 2022-05-25 18:48:40).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 77-121), source close, variation Hma, length 55
    HULL = wma(2 wma(close, 27) - wma(close, 55), round(sqrt(55)))
    HULL > HULL[2] -> entry "buy" (long);  HULL < HULL[2] -> entry "sell" (short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine v4 integer division: 55 / 2 -> 27. The direction input is unused (its
      allow_entry_in line is commented out), so both sides trade. testPeriod() returns true.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365727_hull_suite_slope"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [34, 55, 89, 180],
}
DEFAULT_PARAMS = {"length": 55}


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
    n = int(p["length"])
    hull = _wma(2 * _wma(c, n // 2) - _wma(c, n), int(round(np.sqrt(n))))
    up = (hull > hull.shift(2)).to_numpy()
    dn = (hull < hull.shift(2)).to_numpy()
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
