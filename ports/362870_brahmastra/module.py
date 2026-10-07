"""BRAHMASTRA: a Kalman-smoothed HMA of hl2 against a Kalman-smoothed triple-WMA blend of close;
the blend crossing above goes long, crossing below goes short (always in).
Port of FMZ strategy #362870 "BRAHMASTRA".

Source
    https://www.fmz.com/strategy/362870 (PineScript v4, FMZ last modified 2022-05-13 15:26:38).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 67-141), price hl2, length 22, Kalman on, gain 0.7
    hma(x, p)  = wma(2 * wma(x, p / 2) - wma(x, p), round(sqrt(p)))
    hma3()     = p = length / 2: wma(wma(close, p / 3) * 3 - wma(close, p / 2) - wma(close, p), p)
    kahlman(x, g): dk = x - nz(kf[1], x); smooth = nz(kf[1], x) + dk * sqrt(2g)
                   velo := nz(velo[1]) + g * dk; kf := smooth + velo
    a = kahlman(hma(price, 22), 0.7);  b = kahlman(hma3(), 0.7)
    crossup = b > a and b[1] < a[1] -> entry long; else crossdn = a > b and a[1] < b[1] -> short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine v4 divides integers to integers, so the WMA lengths are floored (22 -> 11, 11 / 3 -> 3,
      11 / 2 -> 5). The Kalman state starts at the first defined input.
    * The trendline module (pivots, slopes, lines) only draws; not ported.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "2h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362870_brahmastra_kalman_hma_cross"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [16, 22, 30],
    "gain": [0.5, 0.7, 1.0],
}
DEFAULT_PARAMS = {"length": 22, "gain": 0.7}


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


def _kalman(x, g):
    v = x.to_numpy(dtype=float)
    kf = np.full(len(v), np.nan)
    velo_prev = np.nan
    for i in range(len(v)):
        base = kf[i - 1] if i and not np.isnan(kf[i - 1]) else v[i]
        dk = v[i] - base
        velo = (0.0 if np.isnan(velo_prev) else velo_prev) + g * dk
        kf[i] = base + dk * np.sqrt(g * 2) + velo
        velo_prev = velo
    return pd.Series(kf, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n, g = int(p["length"]), float(p["gain"])
    c = bars_df["close"]
    price = (bars_df["high"] + bars_df["low"]) / 2
    hma = _wma(2 * _wma(price, n // 2) - _wma(price, n), int(round(np.sqrt(n))))
    q = n // 2
    hma3 = _wma(_wma(c, q // 3) * 3 - _wma(c, q // 2) - _wma(c, q), q)
    a, b = _kalman(hma, g), _kalman(hma3, g)
    up = ((b > a) & (b.shift(1) < a.shift(1))).to_numpy()
    dn = ((a > b) & (a.shift(1) < b.shift(1))).to_numpy()
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
