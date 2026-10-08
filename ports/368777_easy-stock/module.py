"""Easy stock (Zer3192): the 100-bar linear regression of the close crossing above the weekly
triple-WMA hull (shifted one week) goes long; crossing below goes short (always in).
Port of FMZ strategy #368777 "Easy stock".

Source
    https://www.fmz.com/strategy/368777 (PineScript v4, author Zer3192, FMZ last modified
    2022-06-12 21:13:20). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 39-75), timeframe W, period 24, shift 1, len 100
    hma3 = wma(wma(close, 4) * 3 - wma(close, 6) - wma(close, 12), 12)   (p = 24 / 2 = 12, v4 ints)
    b = security("W", hma3[1])   (lookahead off)
    lr = linreg(close, 100, 0)
    crossover(lr, b) -> entry long; else crossunder(lr, b) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Weekly bars are built from the port's 4-hour bars (weeks from Monday 00:00 UTC). With
      lookahead off a historical bar sees the last completed week, whose expression value is
      hma3 one week earlier (the [shift] inside the request).
    * The other weekly HMA (a) only draws.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_368777_linreg_vs_weekly_hull"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [12, 24, 36],
    "len": [50, 100],
}
DEFAULT_PARAMS = {"length": 24, "shift": 1, "len": 100}


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


def _linreg(y, n, offset=0):
    """ta.linreg(y, n, offset): least-squares line over the last n values (x = 0..n-1),
    evaluated at x = n-1-offset."""
    v = y.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        k = np.arange(n, dtype=float)
        sxy = np.convolve(v, k[::-1], mode="full")[n - 1:len(v)]   # sum_k k * v[t-n+1+k]
        sy = np.convolve(v, np.ones(n), mode="full")[n - 1:len(v)]
        slope = (n * sxy - k.sum() * sy) / (n * (k * k).sum() - k.sum() ** 2)
        intercept = (sy - slope * k.sum()) / n
        out[n - 1:] = intercept + slope * (n - 1 - offset)
    return pd.Series(out, index=y.index)


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
    idx = bars_df.index
    week = (idx - pd.to_timedelta(idx.weekday, unit="D")).normalize()
    wk = bars_df.groupby(week).agg({"close": "last"})
    q = int(p["length"]) // 2
    wc = wk["close"]
    hma3 = _wma(_wma(wc, q // 3) * 3 - _wma(wc, q // 2) - _wma(wc, q), q).shift(int(p["shift"]))
    ends = (wk.index + pd.Timedelta(days=7)).asi8
    close_time = (idx + pd.Timedelta(FREQ)).asi8
    pos = np.searchsorted(ends, close_time, side="right") - 1
    b = np.where(pos >= 0, hma3.to_numpy()[np.clip(pos, 0, None)], np.nan)
    lr = _linreg(bars_df["close"], int(p["len"]), 0).to_numpy()
    lag = lambda a: np.concatenate([[np.nan], a[:-1]])
    buy = (lr > b) & (lag(lr) <= lag(b))
    sell = (lr < b) & (lag(lr) >= lag(b))
    return _always_in(buy, sell, idx)


def portfolio_kwargs(**params):
    return {}
