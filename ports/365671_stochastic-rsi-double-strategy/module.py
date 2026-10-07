"""Stochastic + RSI double (ChartArt): %K crossing above %D below 20 together with RSI crossing
above 30 goes long; %K crossing below %D above 80 with RSI crossing below 70 goes short.
Port of FMZ strategy #365671 "Stochastic + RSI, Double Strategy (by ChartArt)".

Source
    https://www.fmz.com/strategy/365671 (PineScript v2/v3 syntax, FMZ last modified 2022-05-25 16:12:14).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 76-104), stoch 14 / 3 / 3 (80 / 20), RSI 14 (70 / 30)
    long  = crossover(k, d) and k < 20 and crossover(rsi, 30) -> entry long
    short = crossunder(k, d) and k > 80 and crossunder(rsi, 70) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365671_stoch_rsi_double_cross"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stoch_len": [9, 14],
    "rsi_len": [7, 14],
    "smooth": [3, 5],
}
DEFAULT_PARAMS = {"stoch_len": 14, "smooth": 3, "rsi_len": 14}


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
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, s = int(p["stoch_len"]), int(p["smooth"])
    st = 100 * (c - l.rolling(n).min()) / (h.rolling(n).max() - l.rolling(n).min())
    k = st.rolling(s).mean()
    d = k.rolling(s).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    up = (k > d) & (k.shift(1) <= d.shift(1)) & (k < 20) & (rsi > 30) & (rsi.shift(1) <= 30)
    dn = (k < d) & (k.shift(1) >= d.shift(1)) & (k > 80) & (rsi < 70) & (rsi.shift(1) >= 70)
    return _always_in(up.to_numpy(), dn.to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
