"""Classic Supertrend (ATR 10 x 3 on hl2) flips, 1-hour bars: the trend turning up goes long, turning down goes short; reversing.
Port of FMZ strategy #454742 "SuperTrend策略优化动态波动率跟踪与交易信号增强系统-SuperTrend-Strategy-Optimization-Dynamic-Volatility-Tracking-and-Enhanced-Trading-Signal-System" (SuperTrend STRATEGY with Buy/Sell Conditions).

FMZ source id: 454742

Source
    https://www.fmz.com/strategy/454742 (PineScript v4, FMZ last modified 2024-06-21 15:30:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 152-244), Supertrend ATR 10 (changeATR true: rma), multiplier 3, hl2; trading window 2018-9999
    trend turns 1 (from -1) -> entry BUY;  trend turns -1 (from 1) -> entry SELL

Interpretation choices (Pine rules in SURVEY_README.md)
    * The classic Supertrend recursion as written. The trading window (from 2018 to 9999) is dropped
      like other date windows. The alert flags and bar colours are display only. REVERSAL INTENDED. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Supertrend flips.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND427399 (3 members, best partner #428578, Jaccard 0.713); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the date window dropped).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_454742_classic_supertrend_flip_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_len": [10, 14],
    "mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"atr_len": 10, "mult": 3.0}


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


def _classic_trend(bars_df, n, k):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(n)).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    upv, dnv, trend = np.full(m, np.nan), np.full(m, np.nan), np.ones(m, dtype=int)
    t = 1
    for i in range(m):
        up, dn = hl2[i] - k * atr[i], hl2[i] + k * atr[i]
        up1 = upv[i - 1] if i > 0 and not np.isnan(upv[i - 1]) else up
        dn1 = dnv[i - 1] if i > 0 and not np.isnan(dnv[i - 1]) else dn
        cp = cv[i - 1] if i > 0 else np.nan
        if cp > up1:
            up = max(up, up1)
        if cp < dn1:
            dn = min(dn, dn1)
        if t == -1 and cv[i] > dn1:
            t = 1
        elif t == 1 and cv[i] < up1:
            t = -1
        upv[i], dnv[i], trend[i] = up, dn, t
    return trend


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    tr = pd.Series(_classic_trend(bars_df, p["atr_len"], float(p["mult"])), index=bars_df.index)
    t1 = tr.shift(1)
    le = (tr == 1) & (t1 == -1)
    se = (tr == -1) & (t1 == 1)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
