"""Doubled Ichimoku, long only: Tenkan above Kijun, the close above both (undisplaced) spans of a
green cloud, the close above both spans 61 bars back and above the close 30 bars back go long;
the close dropping under a span 30 bars back, under the close 30 bars back, or under Kijun
closes the long.
Port of FMZ strategy #426797 "Ichimoku Trading Strategy".

Source
    https://www.fmz.com/strategy/426797 (PineScript v4, FMZ last modified 2023-09-14 16:13:33).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 122-157), 20 / 60 / 120, displacement 30
    conv = donchian(20); base = donchian(60); A = avg(conv, base); B = donchian(120)
    long = conv > base and close > A and close > B and A > B
           and close > A[61] and close > B[61] and close > close[30]
    close_trade = crossover(A[30], close) or crossover(B[30], close) or close < close[30]
                  or crossover(base, close)
    long -> entry long;  close_trade -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * position_count = 1 / = 0 inside the if-blocks declare new local variables (= not :=), so
      the var stays 0 and never blocks an entry (as written).
    * Same bar: from flat the entry stands (close_all finds no position at the close); while
      long the entry is refused and close_all goes flat. The stop-loss input is unused.
    * Long only. FREQ = "2h" from the backtest header (spot BTC_USDT in the header).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426797_doubled_ichimoku_long"
FAMILY = "ichimoku"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conv": [9, 20],
    "base": [26, 60],
    "span_b": [52, 120],
    "disp": [26, 30],
}
DEFAULT_PARAMS = {"conv": 20, "base": 60, "span_b": 120, "disp": 30}


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


def _xover(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    don = lambda n: (l.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2
    conv, base = don(p["conv"]), don(p["base"])
    a, b = (conv + base) / 2, don(p["span_b"])
    k = int(p["disp"])
    lag = 2 * k + 1
    entry = ((conv > base) & (c > a) & (c > b) & (a > b)
             & (c > a.shift(lag)) & (c > b.shift(lag)) & (c > c.shift(k))).to_numpy()
    out = (_xover(a.shift(k), c) | _xover(b.shift(k), c) | (c < c.shift(k)) | _xover(base, c)).to_numpy()
    target = np.zeros(len(c), dtype=int)
    pos = 0
    for i in range(len(c)):
        if pos == 0 and entry[i]:
            pos = 1
        elif pos == 1 and out[i]:
            pos = 0
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
