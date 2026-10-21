"""Smoothed 200-bar extremes with ATR offsets, 1-hour bars: the close crossing over the 10-bar SMA of the 200-bar high goes long, crossing under that line minus 2 ATR closes the long; the close crossing under the
SMA of the 200-bar low goes short, crossing over that line plus 2 ATR closes the short.
Port of FMZ strategy #437761 "Trend Following Moving Average Trading Strategy" (I Like Winners And Love Loosers!).

FMZ source id: 437761

Source
    https://www.fmz.com/strategy/437761 (PineScript v4, FMZ last modified 2024-01-05 13:48:07).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 145-169), highest 200 / average 10, lowest 200 / average 10, ATR 14 x 2
    h1 = sma(highest(high, 200), 10), l1 = h1 - 2 atr;  h2 = sma(lowest(low, 200), 10), l2 = h2 + 2 atr
    crossover(close, h1) -> entry Buy;  crossunder(close, l1) -> close Buy;  crossunder(close, h2) -> entry Sell;  crossover(close, l2) -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Orders follow the script's call order (entry Buy, close Buy, entry Sell, close Sell); a close only acts
      on the position open at the bar's close and left unchanged by the entries. REVERSAL INTENDED. The 100 %
      of equity size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed extremes with ATR offsets.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437761_smoothed_extreme_atr_bands"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [200, 100],
    "atr_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"length": 200, "average": 10, "atr_len": 14, "atr_mult": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    a = _rma(tr, int(p["atr_len"])) * float(p["atr_mult"])
    n, k = int(p["length"]), int(p["average"])
    h1 = h.rolling(n).max().rolling(k).mean()
    l1 = h1 - a
    h2 = lo.rolling(n).min().rolling(k).mean()
    l2 = h2 + a

    def xo(x, y):
        return ((x > y) & (x.shift(1) <= y.shift(1))).to_numpy()

    def xu(x, y):
        return ((x < y) & (x.shift(1) >= y.shift(1))).to_numpy()

    lc, lxc, sc, sxc = xo(c, h1), xu(c, l1), xu(c, h2), xo(c, l2)
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        s, changed = pos, False
        if lc[i] and s != 1:
            s, changed = 1, True
        if lxc[i] and pos == 1 and not changed:
            s = 0
        if sc[i] and s != -1:
            s, changed = -1, True
        if sxc[i] and pos == -1 and not changed:
            s = 0
        if s == 1 and pos != 1:
            le[i] = True
        elif s == -1 and pos != -1:
            se[i] = True
        elif s == 0 and pos == 1:
            lx[i] = True
        elif s == 0 and pos == -1:
            sx[i] = True
        pos = s
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
