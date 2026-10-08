"""Combo 123 Reversal & Relative Volatility Index (HPotter): long when both the 123-reversal state
and the RVI state are +1, short when both are -1, flat otherwise.
Port of FMZ strategy #426322 "Combo Backtest 123 Reversal Relative Volatility Index".

Source
    https://www.fmz.com/strategy/426322 (PineScript v4, FMZ last modified 2023-09-11 09:01:03).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 89-136), 14 / 1 / 3 / 50, RVI 10 / 30 / 70
    vFast = sma(stoch(close, high, low, 14), 1); vSlow = sma(vFast, 3)
    pos123 = +1 if close[2] < close[1] < close and vFast < vSlow and vFast > 50,
             -1 if close[2] > close[1] > close and vFast > vSlow and vFast < 50, else previous
    sd = stdev(close, 10); u = close > close[1] ? sd : 0; d = close > close[1] ? 0 : sd
    nU = (13 nU[1] + u) / 14; nD likewise; nRes = 100 nU / (nU + nD)
    posRVI = -1 if nRes < 30, +1 if nRes > 70, else previous
    both +1 -> entry long; both -1 -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written, RVI below the buy zone gives -1 and above the sell zone +1 (HPotter's code).
    * nz(nU[1]) / nz(nD[1]): the recursions restart from 0 after the stdev warm-up (na inputs
      give na, as Pine). stdev is Pine's population deviation; stoch over a flat range is na.
    * "Trade reverse" is off (source default). strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426322_combo_123_reversal_rvi"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21],
    "rvi_period": [10, 14],
    "buy_zone": [30, 40],
}
DEFAULT_PARAMS = {"length": 14, "k_smooth": 1, "d_length": 3, "level": 50,
                  "rvi_period": 10, "buy_zone": 30, "sell_zone": 70}


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


def _pos_123(bars, p):
    h, l, c = bars["high"], bars["low"], bars["close"]
    n = int(p["length"])
    lo, hi = l.rolling(n).min(), h.rolling(n).max()
    stoch = 100 * (c - lo) / (hi - lo)
    fast = stoch.rolling(int(p["k_smooth"])).mean()
    slow = fast.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    up = ((c2 < c1) & (c > c1) & (fast < slow) & (fast > p["level"])).to_numpy()
    dn = ((c2 > c1) & (c < c1) & (fast > slow) & (fast < p["level"])).to_numpy()
    out = np.zeros(len(c))
    prev = 0.0
    for i in range(len(c)):
        prev = 1.0 if up[i] else (-1.0 if dn[i] else prev)
        out[i] = prev
    return out


def _pos_rvi(close, p):
    sd = close.rolling(int(p["rvi_period"])).std(ddof=0).to_numpy()
    rising = (close > close.shift(1)).to_numpy()
    m = len(close)
    out = np.zeros(m)
    nu_prev = nd_prev = np.nan
    prev = 0.0
    for i in range(m):
        u = sd[i] if rising[i] else 0.0
        d = 0.0 if rising[i] else sd[i]
        nu = (13 * (0.0 if np.isnan(nu_prev) else nu_prev) + u) / 14
        nd = (13 * (0.0 if np.isnan(nd_prev) else nd_prev) + d) / 14
        res = 100 * nu / (nu + nd) if (nu + nd) != 0 else np.nan
        if res < p["buy_zone"]:
            prev = -1.0
        elif res > p["sell_zone"]:
            prev = 1.0
        out[i] = prev
        nu_prev, nd_prev = nu, nd
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _pos_123(bars_df, p)
    b = _pos_rvi(bars_df["close"], p)
    target = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0))
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
