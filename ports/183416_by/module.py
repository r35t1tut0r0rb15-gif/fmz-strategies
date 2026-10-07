"""Regression slope of a smoothed channel midpoint: long while the slope rises, short while it
falls (always in, reverses on every change of slope direction).
Port of FMZ strategy #183416 "定量分型速率交易策略-by泊宇量化" (fractal rate strategy).

Source
    https://www.fmz.com/strategy/183416 (MyLanguage, author "homily", FMZ last modified
    2021-02-08 13:47:31). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 33-44), len 35
    hh = HHV(H,len); ll = LLV(L,len); hl2 = (hh+ll)/2; avg = MA(hl2,5)
    ss = SLOPE(avg,len)                      (least-squares slope over len bars, current included)
    ss < REF(ss,1) -> SPK;   ss > REF(ss,1) -> BPK;   AUTOFILTER

Interpretation choices (MyLanguage rules in SURVEY_README.md)
    * Close-price model, completed bars. BPK/SPK reverse in one bar: REVERSAL INTENDED
      (portfolio_kwargs {}; the engine's default opposite-entry reversal applies). Equal slopes
      give no signal; the SPK line is first in the source.
    * The slope is in price units per bar, but only its change of sign matters, so criterion 2
      PASS. Lot size `liang` (half of equity x previous close / 100, doubled for shorts) is sizing.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_183416_channel_mid_slope_reverse"
FAMILY = "slope_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 35, 50],
    "smooth": [3, 5, 8],
}
DEFAULT_PARAMS = {"length": 35, "smooth": 5}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _slope(y, n):
    """Least-squares slope of the last n values (x = 0..n-1), current value included."""
    v = y.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        k = np.arange(n, dtype=float)
        sxy = np.convolve(v, k[::-1], mode="full")[n - 1:len(v)]   # sum_k k * v[t-n+1+k]
        sy = np.convolve(v, np.ones(n), mode="full")[n - 1:len(v)]
        out[n - 1:] = (n * sxy - k.sum() * sy) / (n * (k * k).sum() - k.sum() ** 2)
    return pd.Series(out, index=y.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    hl2 = (bars_df["high"].rolling(n).max() + bars_df["low"].rolling(n).min()) / 2
    ss = _slope(hl2.rolling(int(p["smooth"])).mean(), n)
    down = (ss < ss.shift(1)).to_numpy()
    up = (ss > ss.shift(1)).to_numpy()

    m = len(bars_df)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if down[i] and pos != -1:     # SPK
            se[i], pos = True, -1
        elif up[i] and pos != 1:      # BPK
            le[i], pos = True, 1

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
