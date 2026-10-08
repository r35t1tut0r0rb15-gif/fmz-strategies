"""Noro's CryptoBottom, long only: a red bar far below SMA 10 (more than 3x the 100-bar average
distance), making a lower body low, with the 2-bar RSI under 10 goes long; any bar whose high
reaches SMA 5 closes it.
Port of FMZ strategy #426990 "Bottom Following Trading Strategy".

Source
    https://www.fmz.com/strategy/426990 (PineScript v2/v3 syntax, FMZ last modified 2023-09-16 18:37:44).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 136-161)
    len = |close - sma(close, 10)|; up = close < open and len > 3 sma(len, 100)
          and min(open, close) < its previous value and fastrsi(2) < 10
    dn = high > sma(close, 5)
    up -> entry long;  dn -> entry "Exit" short with qty 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * A short entry of qty 0 reverses the long and opens nothing: an exit (Noro's idiom). Both
      orders fill in issue order, so a bar with both signals ends flat. Long only.
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426990_noro_crypto_bottom_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "dist_mult": [2.0, 3.0],
    "rsi_level": [10, 20],
}
DEFAULT_PARAMS = {"dist_mult": 3.0, "rsi_level": 10}


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


def _rsi_pine(close, n):
    """rsi() as Pine defines it: 100 when the average loss is 0, 0 when the average gain is 0."""
    d = close.diff()
    up, down = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    rsi = 100.0 - 100.0 / (1.0 + up / down)
    return rsi.mask(up == 0, 0.0).mask(down == 0, 100.0).where(up.notna() & down.notna())


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
    o, h, c = bars_df["open"], bars_df["high"], bars_df["close"]
    rsi = _rsi_pine(c, 2)
    dist = (c - c.rolling(10).mean()).abs()
    mn = np.minimum(o, c)
    up = ((c < o) & (dist > dist.rolling(100).mean() * p["dist_mult"]) & (mn < mn.shift(1))
          & (rsi < p["rsi_level"])).to_numpy()
    dn = (h > c.rolling(5).mean()).to_numpy()
    target = np.zeros(len(c), dtype=int)
    pos = 0
    for i in range(len(c)):
        if up[i]:
            pos = 1
        if dn[i]:
            pos = 0
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
