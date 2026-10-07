"""Fibonacci progression with breaks (LuxAlgo): a reference level steps through Fibonacci
multiples of ATR(200) each time price moves that far from it; after the sequence is exhausted
the level resets to the close. A reset upward goes long, downward goes short (always in).
Port of FMZ strategy #363749 "Fibonacci Progression With Breaks [LUX]".

Source
    https://www.fmz.com/strategy/363749 (PineScript v5, FMZ last modified 2022-05-17 10:41:56).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 63-108), method Atr, size 1, sequence length 3
    fib = [1, 1, 2, 3, 5];  dist = atr(200) * size * fib[fib_n]
    fib_n := |close - avg| > dist ? fib_n + 1 : fib_n
    avg := nz(fib_n > max + 1 ? close : avg[1], close);  fib_n := fib_n > max + 1 ? 1 : fib_n
    avg > avg[1] -> entry long; else avg < avg[1] -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "Manual" method (size in price units) is not the default and is not ported; the ATR
      method is already scale-free. Before ATR(200) exists the level holds the first close.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "5min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_363749_fibonacci_progression_breaks"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
ATR_LEN = 200

GRID = {
    "size": [0.5, 1.0, 2.0],
    "seq_len": [2, 3, 4],
}
DEFAULT_PARAMS = {"size": 1.0, "seq_len": 3}


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


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


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
    mx = int(p["seq_len"])
    fib = [1, 1]
    for i in range(1, mx + 1):
        fib.append(fib[i - 1] + fib[i])
    atr = _atr_pine(bars_df, ATR_LEN).to_numpy()
    c = bars_df["close"].to_numpy(dtype=float)
    m = len(c)
    avg = np.full(m, np.nan)
    fib_n = 1
    for i in range(m):
        dist = atr[i] * p["size"] * fib[fib_n]
        prev = avg[i - 1] if i else np.nan
        if not np.isnan(prev) and abs(c[i] - prev) > dist:
            fib_n += 1
        a = c[i] if fib_n > mx + 1 else prev
        avg[i] = c[i] if np.isnan(a) else a
        if fib_n > mx + 1:
            fib_n = 1
    prev = np.concatenate([[np.nan], avg[:-1]])
    return _always_in(avg > prev, avg < prev, bars_df.index)


def portfolio_kwargs(**params):
    return {}
