"""SMA 10 / 50 crossings with an RSI 14 filter, 1-hour bars: the cross up with the RSI under 70 goes long, the cross down with the RSI over 30 goes short; an RSI over 70 closes the long, under 30 the short; reversing.
Port of FMZ strategy #454741 "机器学习启发的双均线RSI交易策略-Machine-Learning-Inspired-Dual-Moving-Average-RSI-Trading-Strategy" (ML Inspired Strategy for Nifty50).

FMZ source id: 454741

Source
    https://www.fmz.com/strategy/454741 (PineScript v5, FMZ last modified 2024-06-21 15:27:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 152-193), SMA 10 / 50; RSI 14, levels 70 / 30
    crossover(sma10, sma50) and rsi < 70 -> entry Long;  crossunder and rsi > 30 -> entry Short;  rsi > 70 -> close Long;  rsi < 30 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are called before the closes; an opposite entry reverses and the close then finds the
      trade reversed; a close acts only on the trade held into the bar. REVERSAL INTENDED. No sizing
      code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with RSI exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_454741_sma10_50_cross_rsi_exit_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 20],
    "slow": [50, 100],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 50, "rsi_len": 14, "ob": 70.0, "os": 30.0}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a = c.rolling(int(p["fast"])).mean()
    b = c.rolling(int(p["slow"])).mean()
    r = _rsi(c, int(p["rsi_len"]))
    ob, os_ = float(p["ob"]), float(p["os"])
    el = ((a > b) & (a.shift(1) <= b.shift(1)) & (r < ob)).to_numpy()
    es = ((a < b) & (a.shift(1) >= b.shift(1)) & (r > os_)).to_numpy()
    xl, xs = (r > ob).to_numpy(), (r < os_).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        cur = pos
        if el[i] and cur != 1:
            cur = 1
        if es[i] and cur != -1:
            cur = -1
        if xl[i] and pos == 1 and cur == 1:
            cur = 0
        if xs[i] and pos == -1 and cur == -1:
            cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
