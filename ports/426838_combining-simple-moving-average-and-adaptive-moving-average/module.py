"""IIR / ALMA cross, long only: from flat, a 3-pole IIR filter of the close crossing above its
ALMA, with a much longer IIR rising, goes long; the IIR crossing back under its ALMA closes it.
Port of FMZ strategy #426838 "Combining Simple Moving Average and Adaptive Moving Average".

Source
    https://www.fmz.com/strategy/426838 (PineScript v4, FMZ last modified 2023-09-14 18:14:34).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 297-498), IIRx 13 / 21, IIRx2 144 / 233, ALMA 21 / 0.99 / 8
    multiplier(res, len) = round(len * res / timeframe.multiplier)    (5 on the 5-minute bars)
    iirma(n, src): cf = 2 tan(pi / n); 3-pole recursion seeded with nz(..., src)
    fast = iirma(round(13 * 21 / 5), close); slow = iirma(round(144 * 233 / 5), close)
    alma = alma(fast, 21, 0.99, 8)
    crossover(fast, alma) and slow > slow[1] -> open long (if no open trade)
    crossunder(fast, alma)                   -> close (if a trade is open)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The filter lengths scale with timeframe.multiplier as written: 55 and 6710 bars on the
      5-minute header bars.
    * The MA fan counts, squeeze colours, RSI arrows and debug panels do not reach the orders.
    * Long only (positionType "LONG"). FREQ = "5min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426838_iir_alma_cross_long"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
TF_MULT = 5  # timeframe.multiplier of FREQ

GRID = {
    "iirx": [8, 13],
    "iirx2": [89, 144],
    "alma_period": [21, 34],
}
DEFAULT_PARAMS = {"iirx": 13, "iirx_period": 21, "iirx2": 144, "iirx2_period": 233,
                  "alma_period": 21, "alma_offset": 0.99, "alma_sigma": 8.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _iirma(x, n):
    cf = 2 * np.tan(2 * 3.14159 * (1 / n) / 2)
    a0 = 8 + 8 * cf + 4 * cf ** 2 + cf ** 3
    a1 = -24 - 8 * cf + 4 * cf ** 2 + 3 * cf ** 3
    a2 = 24 - 8 * cf - 4 * cf ** 2 + 3 * cf ** 3
    a3 = -8 + 8 * cf - 4 * cf ** 2 + cf ** 3
    c, d0, d1, d2 = cf ** 3 / a0, -a1 / a0, -a2 / a0, -a3 / a0
    s = x.to_numpy(dtype=float)
    out = np.full(len(s), np.nan)
    for i in range(len(s)):
        v = np.nan
        if i >= 3:
            v = (c * (s[i] + s[i - 3]) + 3 * c * (s[i - 1] + s[i - 2])
                 + d0 * out[i - 1] + d1 * out[i - 2] + d2 * out[i - 3])
        out[i] = s[i] if np.isnan(v) else v  # nz(..., src)
    return pd.Series(out, index=x.index)


def _alma(x, n, offset, sigma):
    m = np.floor(offset * (n - 1))
    s = n / sigma
    w = np.exp(-((np.arange(n) - m) ** 2) / (2 * s * s))  # w[0] on the oldest value
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    fast = _iirma(c, int(round(p["iirx"] * p["iirx_period"] / TF_MULT)))
    slow = _iirma(c, int(round(p["iirx2"] * p["iirx2_period"] / TF_MULT)))
    alma = _alma(fast, int(p["alma_period"]), p["alma_offset"], p["alma_sigma"])
    d = fast - alma
    up = ((d > 0) & (d.shift(1) <= 0) & (slow > slow.shift(1))).to_numpy()
    dn = ((d < 0) & (d.shift(1) >= 0)).to_numpy()
    target = np.zeros(len(c), dtype=int)
    pos = 0
    for i in range(len(c)):
        if pos == 0 and up[i]:
            pos = 1
        elif pos == 1 and dn[i]:
            pos = 0
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
