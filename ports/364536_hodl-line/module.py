"""HODL line: HMA 50 of close crossing above the 100-bar close midrange divided by 2.05 (an
asymmetric midline) goes long; crossing below goes short (always in).
Port of FMZ strategy #364536 "HODL LINE".

Source
    https://www.fmz.com/strategy/364536 (PineScript v5, FMZ last modified 2022-05-20 16:59:54).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 58-108), sensitivity "Hold Short Term" (length 100),
asymmetry 0.05, smoothing on (HMA 50)
    HODL = (highest(close, 100) + lowest(close, 100)) / (2 + 0.05)
    crossover(hma(close, 50), HODL) -> entry long; else crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.hma = wma(2 wma(x, n/2) - wma(x, n), round(sqrt(n))). The line is a ratio of price
      (scale-free).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "5min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_364536_hodl_line_cross"
FAMILY = "donchian_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 100, 300, 500],
    "hma_len": [25, 50],
}
DEFAULT_PARAMS = {"length": 100, "hma_len": 50, "asymmetry": 0.05}


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
    line = (c.rolling(n).max() + c.rolling(n).min()) / (2.0 + p["asymmetry"])
    k = int(p["hma_len"])
    hma = _wma(2 * _wma(c, k // 2) - _wma(c, k), int(round(np.sqrt(k))))
    up = ((hma > line) & (hma.shift(1) <= line.shift(1))).to_numpy()
    dn = ((hma < line) & (hma.shift(1) >= line.shift(1))).to_numpy()
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
