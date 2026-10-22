"""MACD (5, 35, 5) signal crossings with RSI filters, 1-hour bars, long only: MACD crossing over its signal with the RSI 14 under 40 goes long; crossing under with the RSI over 60 closes.
Port of FMZ strategy #442013 "基于MACD与RSI组合策略A-Combined-Strategy-with-MACD-and-RSI" (MRS long).

FMZ source id: 442013

Source
    https://www.fmz.com/strategy/442013 (PineScript v5, FMZ last modified 2024-02-18 16:07:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 154-190), MACD 5 / 35 / 5 (EMAs); RSI 14; the short side is commented out
    buy = crossover(macd, signal) and rsi < 40 -> entry Buy;  sell = crossunder(macd, signal) and rsi > 60 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short entries are commented out. Long only. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crossings with RSI filters.
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

NAME = "fmz_442013_macd5_35_cross_rsi_filter_long"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_length": [5, 12],
    "slow_length": [35, 26],
}
DEFAULT_PARAMS = {"fast_length": 5, "slow_length": 35, "signal_smoothing": 5, "rsi_length": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast_length"]), adjust=False).mean() - c.ewm(span=int(p["slow_length"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal_smoothing"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    up = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (r < 40)
    dn = (macd < sig) & (macd.shift(1) >= sig.shift(1)) & (r > 60)
    false = pd.Series(False, index=c.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
