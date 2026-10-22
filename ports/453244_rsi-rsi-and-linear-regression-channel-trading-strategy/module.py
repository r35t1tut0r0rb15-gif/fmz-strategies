"""Linear-regression channel (100-bar end +- 1 SD) extremes with RSI 14 confirmation, 1-hour bars, long only: a close at or under the lower line with the RSI under 30 buys; a close at or over the upper line with the RSI over 70 sells.
Port of FMZ strategy #453244 "RSI与线性回归通道交易策略-RSI-and-Linear-Regression-Channel-Trading-Strategy" (RSI and Linear Regression Channel Strategy).

FMZ source id: 453244

Source
    https://www.fmz.com/strategy/453244 (PineScript v5, FMZ last modified 2024-06-03 11:19:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-126), linreg 100 +- stdev 100; RSI 14, levels 30 / 70
    close <= linreg - sd and rsi < 30 -> entry Long;  close >= linreg + sd and rsi > 70 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both tests are states (a repeat entry while long is ignored); they cannot meet on one bar. Long
      only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, regression-channel extremes with RSI confirmation.
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

NAME = "fmz_453244_linreg_channel_rsi_extreme_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "channel_len": [100, 50],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"channel_len": 100, "rsi_len": 14, "os": 30.0, "ob": 70.0}


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


def _linreg_end(s, n):
    n = int(n)
    w = np.arange(n, dtype=float) - (n - 1) / 2.0
    sxx = float(np.dot(w, w))
    return s.rolling(n).apply(lambda a: float(a.mean() + np.dot(w, a) / sxx * (n - 1) / 2.0), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["channel_len"])
    basis = _linreg_end(c, n)
    sd = c.rolling(n).std(ddof=0)
    r = _rsi(c, int(p["rsi_len"]))
    le = (c <= basis - sd) & (r < float(p["os"]))
    lx = (c >= basis + sd) & (r > float(p["ob"]))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
