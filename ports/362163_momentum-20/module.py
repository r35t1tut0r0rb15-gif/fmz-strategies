"""Momentum 2.0: volatility-normalised momentum (smoothed by linear regression) crossing its own
negative long EMA, stop-and-reverse.
Port of FMZ strategy #362163 "Momentum-20".

Source
    https://www.fmz.com/strategy/362163 (PineScript v5, FMZ last modified 2022-05-10 10:32:54).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 55-76), window 15, base 450
    mom = close - close[15]; norm = mom / stdev(mom, 450); smooth = linreg(norm, 30, 0)
    base = -ema(norm, 450)
    crossover(smooth, base) -> entry long;  else crossunder(smooth, base) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * stdev over a rolling 450-bar window ending at the current bar (population).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362163_normalised_momentum_cross"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "window": [10, 15, 30],
    "base_window": [300, 450, 600],
}
DEFAULT_PARAMS = {"window": 15, "base_window": 450, "smooth": 30}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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
    c = bars_df["close"]
    w, b = int(p["window"]), int(p["base_window"])
    mom = c - c.shift(w)
    norm = (mom / mom.rolling(b).std(ddof=0)).replace([np.inf, -np.inf], np.nan)
    sm = _linreg(norm, int(p["smooth"]), 0)
    base = -norm.ewm(span=b, adjust=False, ignore_na=True).mean()
    up = ((sm > base) & (sm.shift(1) <= base.shift(1))).to_numpy()
    dn = ((sm < base) & (sm.shift(1) >= base.shift(1))).to_numpy()
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
