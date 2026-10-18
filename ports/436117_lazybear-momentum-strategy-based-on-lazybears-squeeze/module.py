"""Squeeze-momentum slope turns, 1-hour bars, long only: the sign of the 2-bar change of the LazyBear squeeze momentum crossing from non-positive to positive, with the close over the
EMA 50 and the EMA rising, goes long; the sign turning negative closes the long.
Port of FMZ strategy #436117 "基于LazyBear压力矩量化动量策略Momentum-Strategy-Based-on-LazyBears-Squeeze" (Crypto momentum strategy).

FMZ source id: 436117

Source
    https://www.fmz.com/strategy/436117 (PineScript v4, FMZ last modified 2023-12-21 14:22:49).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 197-246), BB 20 / 2, Keltner 20 / 1.5 (true range); momentum = linear regression of the close minus the channel midpoint; EMA 50
    val = linreg(close - avg(avg(highest(high, 20), lowest(low, 20)), sma(close, 20)), 20, 0);  slope = val - val[2];  co = crossover(slope / |slope|, 0);  cu = crossunder(slope / |slope|, 0)
    co and close > ema50 and ema50 > ema50[1] -> entry long;  cu -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * slope / |slope| is the sign of the slope (missing at zero). linreg is the value at the end of the
      least-squares line. The squeeze flags are only drawn. Long only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, momentum regression and a trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the initial balance input stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436117_squeeze_momentum_slope_long"
FAMILY = "momentum_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 30],
    "ema_len": [50, 100],
}
DEFAULT_PARAMS = {"length": 20, "ema_len": 50}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _linreg_end(s, n):
    x = np.arange(n, dtype=float)
    xm = x.mean()
    sxx = ((x - xm) ** 2).sum()

    def f(a):
        return a.mean() + (np.dot(x - xm, a) / sxx) * (n - 1 - xm)

    return s.rolling(n).apply(f, raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    mid = ((h.rolling(n).max() + lo.rolling(n).min()) / 2 + c.rolling(n).mean()) / 2
    val = _linreg_end(c - mid, n)
    slope = val - val.shift(2)
    with np.errstate(invalid="ignore", divide="ignore"):
        sgn = slope / slope.abs()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    co = (sgn > 0) & (sgn.shift(1) <= 0)
    cu = (sgn < 0) & (sgn.shift(1) >= 0)
    le = (co & (c > ema) & (ema > ema.shift(1))).fillna(False).astype(bool)
    lx = cu.fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
