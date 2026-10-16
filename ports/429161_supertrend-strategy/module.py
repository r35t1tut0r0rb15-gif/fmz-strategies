"""SuperTrend (chandelier-style ATR stops), long only, 4-hour bars: a flip to up-trend goes long, a flip to
down-trend closes the long.
Port of FMZ strategy #429161 "SuperTrend Strategy" (SuperTrend Strategy).

FMZ source id: 429161

Source
    https://www.fmz.com/strategy/429161 (PineScript v4, FMZ last modified 2023-10-13 17:03:55).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 214-288), ATR 22 x 3, Long Only
    longStop = hl2 - 3 atr(22), ratcheted up while close[1] > longStop[1]; shortStop = hl2 + 3 atr(22), ratcheted down
    dir flips to 1 when close > shortStop[1], to -1 when close < longStop[1]
    buySignal -> entry long; sellSignal -> close long (Long Only)

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Long Only ?" defaults to true. The strategy() line is commented out. The date window is dropped.
    * The lines are signals, not stop orders. Long only. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out strategy() stored.
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

NAME = "fmz_429161_supertrend_long"
FAMILY = "supertrend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [22, 14],
    "mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"length": 22, "mult": 3.0}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = (p["mult"] * _rma(tr, int(p["length"]))).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ls_, ss_ = np.full(m, np.nan), np.full(m, np.nan)
    d = np.ones(m, dtype=np.int8)
    for i in range(m):
        lraw, sraw = src[i] - atr[i], src[i] + atr[i]
        lp = ls_[i - 1] if i >= 1 and not np.isnan(ls_[i - 1]) else lraw
        sp = ss_[i - 1] if i >= 1 and not np.isnan(ss_[i - 1]) else sraw
        ls_[i] = max(lraw, lp) if i >= 1 and cv[i - 1] > lp else lraw
        ss_[i] = min(sraw, sp) if i >= 1 and cv[i - 1] < sp else sraw
        t = d[i - 1] if i >= 1 else 1
        if t == -1 and cv[i] > sp:
            t = 1
        elif t == 1 and cv[i] < lp:
            t = -1
        d[i] = t
    prev = np.concatenate(([1], d[:-1]))
    idx = bars_df.index
    long_e = pd.Series((d == 1) & (prev == -1), index=idx)
    long_x = pd.Series((d == -1) & (prev == 1), index=idx)
    false = pd.Series(False, index=idx)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
