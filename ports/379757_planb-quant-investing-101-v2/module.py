"""PlanB RSI (Zer3192): after RSI 14 dipped below 50 in the last six bars, a 2-point bounce goes
long; after it topped 90 in the last six bars, a drop below 65 goes short (always in).
Port of FMZ strategy #379757 "PlanB Quant Investing 101".

Source
    https://www.fmz.com/strategy/379757 (PineScript v4, author Zer3192, FMZ last modified
    2023-12-02 17:49:46). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 44-103), sell level 90, drop 65, buy level 50
    buy  = lowest(rsi, 6)[1] < 50 and rsi > lowest(rsi, 6)[1] + 2 -> entry long
    sell = highest(rsi, 6)[1] > 90 and rsi < 65 -> entry short
    optional stop / take-profit (off by default)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both entries on one bar: the later order (short) wins, as Pine fills them in order.
    * The stop / take-profit option defaults to off. strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_379757_planb_rsi_bounce"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sell_level": [80, 90],
    "drop": [60, 65],
    "buy_level": [40, 50],
}
DEFAULT_PARAMS = {"sell_level": 90, "drop": 65, "buy_level": 50, "rsi_len": 14, "window": 6}


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
    r = _rsi(bars_df["close"], int(p["rsi_len"]))
    w = int(p["window"])
    mx, mn = r.rolling(w).max().shift(1), r.rolling(w).min().shift(1)
    sell = ((mx > p["sell_level"]) & (r < p["drop"])).to_numpy()
    buy = ((mn < p["buy_level"]) & (r > mn + 2)).to_numpy()
    return _always_in(buy & ~sell, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
