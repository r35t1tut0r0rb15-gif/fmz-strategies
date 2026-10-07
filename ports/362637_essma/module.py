"""ESSMA: a blend of SMMA, EMA, SMA, WMA, RMA, open and close crossing its own WMA; crossing up
goes long, crossing down goes short (always in).
Port of FMZ strategy #362637 "ESSMA".

Source
    https://www.fmz.com/strategy/362637 (PineScript v5, FMZ last modified 2022-05-12 15:20:54).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 90-145), source close, length 50, all weights 2
    smma  := na(smma[2]) ? sma(src, len) : (smma[2] * (len - 1) + src) / len
    essma = (smma + ema + sma - wma - rma + open + close) / 3      (each on src * w, divided by w)
    sessma = wma(essma, len)
    crossover(essma, sessma) -> entry long; else crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every average is linear in its input, so f(src * w) / w = f(src): the weights cancel and
      are not parameters. "Use ATR" defaults to false and is not ported.
    * The author's SMMA recurses on its value two bars back (smma[2]); kept as written.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362637_essma_cross"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50, 100],
}
DEFAULT_PARAMS = {"length": 50}


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


def _smma2(x, n):
    """The author's smma: SMA while smma[2] is na, then (smma[2] * (n - 1) + x) / n."""
    sma = x.rolling(n).mean().to_numpy()
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    for i in range(len(v)):
        prev2 = out[i - 2] if i >= 2 else np.nan
        out[i] = sma[i] if np.isnan(prev2) else (prev2 * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    c = bars_df["close"]
    essma = (_smma2(c, n) + c.ewm(span=n, adjust=False).mean() + c.rolling(n).mean()
             - _wma(c, n) - _rma(c, n) + bars_df["open"] + c) / 3
    sig = _wma(essma, n)
    up = ((essma > sig) & (essma.shift(1) <= sig.shift(1))).to_numpy()
    down = ((essma < sig) & (essma.shift(1) >= sig.shift(1))).to_numpy()
    return _always_in(up, down, bars_df.index)


def portfolio_kwargs(**params):
    return {}
