"""Volatility-stop (ATR 20 x 2 on closes) up-trend with the close above the EMA 30, hourly bars, long only: such a bar buys from flat; a close at or under the EMA 30 closes.
Port of FMZ strategy #478708 "Volatility Stop Based EMA Trend Following Trading Strategy" (VStop + EMA Strategy).

FMZ source id: 478708

Source
    https://www.fmz.com/strategy/478708 (PineScript v5, FMZ last modified 2025-01-17 15:06:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-155), VStop length 20, multiplier 2; EMA 30
    volStop(close, 20, 2): max / min of closes since the last flip, stop = max - 2 atr (up) or min + 2 atr (down), ratcheting, flips reset;  uptrend and close > ema30 and no open trade -> entry Long;  close <= ema30 and open trade -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * A loop computes the volatility stop as written (its ATR multiple falls back to the true range while
      the ATR is na, and the first stop is the close). The entry and exit conditions cannot hold on one
      bar, and the no-open-trade test only skips a repeat. Long only. No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volatility-stop trend with an EMA filter and exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_478708_vstop20x2_uptrend_ema30_long"
FAMILY = "volatility_stop"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 10],
    "ema_length": [30, 50],
}
DEFAULT_PARAMS = {"length": 20, "ema_length": 30, "multiplier": 2.0}


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


def _vstop(bars_df, n, k):
    """The script's volStop on closes: (uptrend flags per bar)."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, n).to_numpy()
    trv = tr.to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    up_flag = np.zeros(m, dtype=bool)
    if m == 0:
        return up_flag
    mx = mn = cv[0]
    up, stop = True, np.nan
    for i in range(m):
        a = atr[i] * k if not np.isnan(atr[i]) else trv[i]
        mx, mn = max(mx, cv[i]), min(mn, cv[i])
        cand = max(stop, mx - a) if up else min(stop, mn + a)
        stop = cv[i] if np.isnan(cand) else cand
        prev = up
        up = cv[i] - stop >= 0.0
        if up != prev and i > 0:
            mx = mn = cv[i]
            stop = mx - a if up else mn + a
        up_flag[i] = up
    return up_flag


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    up = pd.Series(_vstop(bars_df, int(p["length"]), float(p["multiplier"])), index=c.index)
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    false = pd.Series(False, index=c.index)
    return up & (c > e), c <= e, false, false.copy()


def portfolio_kwargs(**params):
    return {}
