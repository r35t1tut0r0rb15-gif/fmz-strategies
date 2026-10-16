"""ATR Fibonacci bands, 2-hour bars: a bar whose range straddles the upper band (SMA 20 + 1.618 ATR 20)
goes long; a bar straddling the lower band (SMA 20 - 1.618 ATR) goes short.
Port of FMZ strategy #427994 "Bollinger Bands Fibonacci Retracement Trading Strategy".

FMZ source id: 427994

Source
    https://www.fmz.com/strategy/427994 (PineScript v4, FMZ last modified 2023-09-27 16:52:05).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 196-247), length 20, Fibo 1 = 1.618 (buy and sell), no reverse
    upper1 = sma(close, 20) + 1.618 atr(20); lower1 = sma - 1.618 atr
    buy = low < upper1 and high > upper1 -> entry long; sell = low < lower1 and high > lower1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Defaults kept: Fibo 1 for both, reverse switches off; the plot offset does not reach the orders.
    * A bar straddling both bands: both orders, the short last (it wins, as the later order).
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR multiples only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_427994_atr_fibo_band_straddle"
FAMILY = "atr_band_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "fibo": [1.618, 2.618],
}
DEFAULT_PARAMS = {"length": 20, "fibo": 1.618}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n)
    sma = c.rolling(n).mean()
    up1, lo1 = sma + atr * p["fibo"], sma - atr * p["fibo"]
    buy = ((lo < up1) & (h > up1)).to_numpy()
    sell = ((lo < lo1) & (h > lo1)).to_numpy()
    m = len(buy)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if sell[i]:
            pos = -1
        elif buy[i]:
            pos = 1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
