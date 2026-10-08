"""Combo 123 Reversal & smoothed Williams A/D (HPotter): long when the 123-reversal state and the
"Williams A/D above its SMA" state are both +1, short when both are -1, flat otherwise.
Port of FMZ strategy #426888 "Quantitative Trading Strategy with Multi Indicator Confirmation".

Source
    https://www.fmz.com/strategy/426888 (PineScript v2/v3 syntax, FMZ last modified 2023-09-15 11:55:04).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 160-201), 14 / 1 / 3 / 50, WAD SMA 14
    wad = close > nz(close[1]) ? nz(wad[1]) + close - low[1]
        : close < nz(close[1]) ? nz(wad[1]) + close - high[1] : 0
    posWAD = wad > sma(wad, 14) ? 1 : wad < sma(wad, 14) ? -1 : previous
    both +1 -> entry long; both -1 -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written an unchanged close resets the A/D sum to 0. The sum starts from 0 (nz), and the
      SMA comparison cancels that start except after such resets.
    * "Trade reverse" off. strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426888_combo_123_reversal_williams_ad"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21],
    "length_wad": [14, 28],
}
DEFAULT_PARAMS = {"length": 14, "length_wad": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _state(up, dn):
    """HPotter state: +1 on up, -1 on dn (up tested first), else the previous value (0 at start)."""
    out = np.zeros(len(up))
    prev = 0.0
    for i in range(len(up)):
        prev = 1.0 if up[i] else (-1.0 if dn[i] else prev)
        out[i] = prev
    return out


def _pos_123(bars, length=14, k_smooth=1, d_length=3, level=50):
    """HPotter's 123 reversal state (stoch over a flat range is na)."""
    h, l, c = bars["high"], bars["low"], bars["close"]
    lo, hi = l.rolling(int(length)).min(), h.rolling(int(length)).max()
    fast = (100 * (c - lo) / (hi - lo)).rolling(int(k_smooth)).mean()
    slow = fast.rolling(int(d_length)).mean()
    c1, c2 = c.shift(1), c.shift(2)
    return _state(((c2 < c1) & (c > c1) & (fast < slow) & (fast > level)).to_numpy(),
                  ((c2 > c1) & (c < c1) & (fast > slow) & (fast < level)).to_numpy())


def _combo_target(a, b):
    return np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0))


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


def _wad(bars):
    c = bars["close"].to_numpy(dtype=float)
    h, l = bars["high"].to_numpy(dtype=float), bars["low"].to_numpy(dtype=float)
    out = np.full(len(c), np.nan)
    prev = np.nan
    for i in range(len(c)):
        c1 = c[i - 1] if i > 0 else 0.0
        base = 0.0 if np.isnan(prev) else prev
        if c[i] > c1:
            v = base + c[i] - (l[i - 1] if i > 0 else np.nan)
        elif c[i] < c1:
            v = base + c[i] - (h[i - 1] if i > 0 else np.nan)
        else:
            v = 0.0
        out[i] = v
        prev = v
    return pd.Series(out, index=bars.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _pos_123(bars_df, p["length"])
    w = _wad(bars_df)
    ma = w.rolling(int(p["length_wad"])).mean()
    b = _state((w > ma).to_numpy(), (w < ma).to_numpy())
    return _emit(_combo_target(a, b), bars_df.index)


def portfolio_kwargs(**params):
    return {}
