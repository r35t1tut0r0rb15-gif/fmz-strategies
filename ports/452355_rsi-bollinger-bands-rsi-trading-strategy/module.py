"""Bollinger 20 / 2 extremes confirmed by the RSI 14, 1-hour bars, long only: a close under the lower band with the RSI under 30 buys; a close over the upper band with the RSI over 70 sells.
Port of FMZ strategy #452355 "布林带RSI交易策略-Bollinger-Bands-RSI-Trading-Strategy" (Bollinger Bands + RSI Strategy).

FMZ source id: 452355

Source
    https://www.fmz.com/strategy/452355 (PineScript v5, FMZ last modified 2024-05-24 17:24:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-126), Bollinger 20 / 2; RSI 14, levels 30 / 70
    close < lower and rsi < 30 -> entry Buy;  close > upper and rsi > 70 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both tests are states (a repeat entry while long is ignored); they cannot meet on one bar.
      Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band extremes with RSI confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_452355_bollinger_rsi_extreme_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 2.5],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "rsi_len": 14, "os": 30.0, "ob": 70.0}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    r = _rsi(c, int(p["rsi_len"]))
    le = (c < basis - dev) & (r < float(p["os"]))
    lx = (c > basis + dev) & (r > float(p["ob"]))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
