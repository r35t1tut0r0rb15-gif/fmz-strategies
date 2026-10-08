"""Delta-RSI: the slope, at the newest bar, of a degree-2 least-squares polynomial fitted to the last
21 RSI(21) values; crossing above zero goes long, below zero goes short (always in).
Port of FMZ strategy #366641 "Delta-RSI Oscillator Strategy".

Source
    https://www.fmz.com/strategy/366641 (PineScript v4, FMZ last modified 2022-05-30 11:51:02).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 243-340), order 2, RSI 21, window 21, conditions
"Zero-Crossing", RMSE filter off
    J[i, j] = i^j (i = 0..20, oldest = 0);  a = pinv(J) . Y  (QR pseudo-inverse)
    drsi = sum_{i >= 1} i a_i (window - 1)^(i - 1)     (derivative at the newest point)
    crossover(drsi, 0) -> entry long; else crossunder(drsi, 0) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The fit uses a fixed design matrix, so the derivative is a fixed linear filter of the last
      21 RSI values: weights = d . pinv(J), computed once (numpy pinv equals the QR route for this
      full-rank J).
    * The exit conditions only feed alerts; strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_366641_delta_rsi_zero_cross"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "degree": [1, 2, 3],
    "rsi_len": [14, 21],
    "window": [14, 21],
}
DEFAULT_PARAMS = {"degree": 2, "rsi_len": 21, "window": 21}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(close, n):
    d = close.diff()
    return 100.0 - 100.0 / (1.0 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))


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
    w, deg = int(p["window"]), int(p["degree"])
    x = np.arange(w, dtype=float)
    jm = np.vander(x, deg + 1, increasing=True)
    dvec = np.array([0.0] + [i * (w - 1) ** (i - 1) for i in range(1, deg + 1)])
    weights = dvec @ np.linalg.pinv(jm)  # applies to [oldest, ..., newest]
    rsi = _rsi(bars_df["close"], int(p["rsi_len"]))
    drsi = rsi.rolling(w).apply(lambda a: float(np.dot(weights, a)), raw=True)
    up = ((drsi > 0) & (drsi.shift(1) <= 0)).to_numpy()
    dn = ((drsi < 0) & (drsi.shift(1) >= 0)).to_numpy()
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
