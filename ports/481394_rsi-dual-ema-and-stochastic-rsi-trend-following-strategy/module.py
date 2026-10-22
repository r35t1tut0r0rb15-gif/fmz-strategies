"""EMA 9 / 21 crossings with the Stochastic RSI (14 / 14, K 3) in its extreme, hourly bars: the cross up with K under 20 goes long, the cross down with K over 80 goes short; reversing.
Port of FMZ strategy #481394 "双均线与随机RSI趋势跟踪策略-Dual-EMA-and-Stochastic-RSI-Trend-Following-Strategy" (EMA 9/21 + Stoch RSI Strategy).

FMZ source id: 481394

Source
    https://www.fmz.com/strategy/481394 (PineScript v5, FMZ last modified 2025-02-10 16:56:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-164), EMA 9 / 21; RSI 14; Stoch RSI 14, K / D 3; 20 / 80
    crossover(ema9, ema21) and k < 20 -> entry Long;  crossunder and k > 80 -> entry Short;  the opposite signal also closes the held side

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stochastic denominator is floored at 1e-10, as written. The closes coincide with the reversing
      entries. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with Stochastic RSI extremes.
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

NAME = "fmz_481394_ema9_21_cross_stochrsi_extreme_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "rsi_len": 14, "stoch_len": 14, "smooth": 3}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    n = int(p["stoch_len"])
    lo_r, hi_r = r.rolling(n).min(), r.rolling(n).max()
    raw = (r - lo_r) / np.maximum(hi_r - lo_r, 1e-10) * 100.0
    k = raw.rolling(int(p["smooth"])).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (k < 20)
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (k > 80)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
