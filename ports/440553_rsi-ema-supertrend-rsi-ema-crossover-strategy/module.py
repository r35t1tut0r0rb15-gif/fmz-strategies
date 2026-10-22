"""Supertrend momentum longs, 1-hour bars, long only: the close above the supertrend (10, 3) with the RSI 14 above 70 and the close above the EMA 9 goes long; the close under the supertrend closes.
Port of FMZ strategy #440553 "超级趋势RSI与EMA交叉策略SuperTrend-RSI-EMA-Crossover-Strategy" (Supertrend, RSI, and EMA Strategy).

FMZ source id: 440553

Source
    https://www.fmz.com/strategy/440553 (PineScript v5, FMZ last modified 2024-01-31 16:16:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 134-161), supertrend ATR 10, factor 3; RSI 14; EMA 9
    longCondition = close > supertrend and rsi > 70 and close > ema9 -> entry Long;  exitCondition = close < supertrend -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The supertrend line is Pine's ta.supertrend (ATR by RMA). The entry and exit cannot hold together.
      Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, supertrend, RSI and EMA.
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

NAME = "fmz_440553_supertrend_rsi70_ema9_long"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "rsi_length": [14, 7],
}
DEFAULT_PARAMS = {"factor": 3.0, "rsi_length": 14, "atr_period": 10, "ema_length": 9}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _supertrend(h, lo, c, factor, n):
    """Pine's ta.supertrend(factor, atrPeriod): (line, direction), direction -1 up, 1 down."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub = np.full(m, np.nan), np.full(m, np.nan)
    st, d = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        if np.isnan(atr[i]):
            continue
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            dn_dir = True
        elif st[i - 1] == ub[i - 1]:
            dn_dir = not (cv[i] > ub[i])
        else:
            dn_dir = cv[i] < lb[i]
        st[i] = ub[i] if dn_dir else lb[i]
        d[i] = 1.0 if dn_dir else -1.0
    return st, d


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    st, _ = _supertrend(h, lo, c, float(p["factor"]), int(p["atr_period"]))
    st = pd.Series(st, index=c.index)
    r = _rsi(c, int(p["rsi_length"]))
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    buy = (c > st) & (r > 70) & (c > e)
    sell = c < st
    false = pd.Series(False, index=c.index)
    return buy, sell, false, false.copy()


def portfolio_kwargs(**params):
    return {}
