"""Low finder (Zer3192): an extrapolated RSI line (RSI 21 + 5 x its distance from its EMA) crossing
above 0 goes long; the mirrored line crossing below 90 goes short (always in).
Port of FMZ strategy #366391 "Low finder".

Source
    https://www.fmz.com/strategy/366391 (PineScript v4, author Zer3192, FMZ last modified
    2022-05-29 07:41:54). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 37-60), length 21
    rsi = rsi(close, 21); pp = ema(rsi, 21); d = (rsi - pp) * 5
    cc = (rsi + d + pp) / 2;  bb = (rsi - d + pp) / 2
    crossover(cc, 0) -> entry long; else crossunder(bb, 90) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header (spot pair in the header only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_366391_rsi_extrapolated_extremes"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21, 34],
}
DEFAULT_PARAMS = {"length": 21}


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
    n = int(p["length"])
    rsi = _rsi(bars_df["close"], n)
    pp = rsi.ewm(span=n, adjust=False).mean()
    d = (rsi - pp) * 5
    cc, bb = (rsi + d + pp) / 2, (rsi - d + pp) / 2
    up = ((cc > 0) & (cc.shift(1) <= 0)).to_numpy()
    dn = ((bb < 90) & (bb.shift(1) >= 90)).to_numpy()
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
