"""EMA 5 / 20 crosses agreeing with the Supertrend (10, 3) direction, long only, 1-hour bars: EMA 5 crossing above
EMA 20 in a Supertrend up-trend goes long; EMA 5 crossing below EMA 20 in a down-trend closes it.
Port of FMZ strategy #483021 "高级双均线与超级趋势组合交易策略-Advanced-Dual-EMA-and-Supertrend-Combination-Trading-Strategy" (Advanced Supertrend + EMA Strategy).

FMZ source id: 483021

Source
    https://www.fmz.com/strategy/483021 (PineScript v5, FMZ last modified 2025-02-27 17:20:22).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 141-190), EMA 5 / 20, Supertrend ATR 10 x 3
    long = crossover(ema5, ema20) and direction < 0 -> entry long; short = crossunder and direction > 0 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend as TradingView documents it (direction -1 = up-trend). Long only; the source has no shorts.
      No stops. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages and Supertrend (ATR bands).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483021_ema5_20_cross_supertrend_long"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "slow": [20, 50],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 20, "atr_len": 10, "factor": 3.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _supertrend_dir(bars_df, factor, n):
    """ta.supertrend direction (pine_supertrend): -1 up-trend, 1 down-trend; nan comparisons are false."""
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    atr = _atr(bars_df, n).to_numpy(dtype=float)
    src = (h + lo) / 2
    m = len(c)
    dr = np.ones(m)
    prev_u = prev_l = prev_st = np.nan
    for i in range(m):
        up, lw = src[i] + factor * atr[i], src[i] - factor * atr[i]
        pl = 0.0 if np.isnan(prev_l) else prev_l
        pu = 0.0 if np.isnan(prev_u) else prev_u
        pc = c[i - 1] if i > 0 else np.nan
        lw = lw if (lw > pl or pc < pl) else pl
        up = up if (up < pu or pc > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif prev_st == pu:
            d = -1 if c[i] > up else 1
        else:
            d = 1 if c[i] < lw else -1
        dr[i] = d
        prev_u, prev_l, prev_st = up, lw, (lw if d == -1 else up)
    return dr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    d = pd.Series(_supertrend_dir(bars_df, float(p["factor"]), int(p["atr_len"])), index=c.index)
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (d < 0)).astype(bool)
    long_x = ((f < s) & (f.shift(1) >= s.shift(1)) & (d > 0)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
