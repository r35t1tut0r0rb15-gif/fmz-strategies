"""RedK Momentum Bars: momentum "bars" built from SMA10 - SMA50 (close) and WMA3(SMA20 - SMA50)
(open); the bar's high crossing above zero goes long, its low crossing below zero goes short.
Port of FMZ strategy #364001 "[dev]RedK Momentum Bars".

Source
    https://www.fmz.com/strategy/364001 (PineScript v5, FMZ last modified 2022-05-18 11:32:35).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 128-209), fast SMA 10, slow SMA 20, delay 3, filter SMA 50
    c = sma(close, 10) - sma(close, 50);  o = wma(sma(close, 20) - sma(close, 50), 3)
    h = max(o, c); l = min(o, c)
    crossover(h, 0) -> entry long; else crossunder(l, 0) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Zero crossings of MA differences are scale-free.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "3min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_364001_redk_momentum_bars_zero"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 10],
    "slow": [20, 30],
    "filter_len": [50, 100],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 20, "filter_len": 50, "delay": 3}


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
    cs = bars_df["close"]
    flt = cs.rolling(int(p["filter_len"])).mean()
    c = cs.rolling(int(p["fast"])).mean() - flt
    o = _wma(cs.rolling(int(p["slow"])).mean() - flt, int(p["delay"]))
    h, l = np.maximum(o, c), np.minimum(o, c)
    up = ((h > 0) & (h.shift(1) <= 0)).to_numpy()
    dn = ((l < 0) & (l.shift(1) >= 0)).to_numpy()
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
