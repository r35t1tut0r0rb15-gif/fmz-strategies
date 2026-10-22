"""Smoothed RSI crossings, 1-hour bars, long only: the 5-bar SMA of the RSI 5 crossing over 40 goes long, crossing under 80 closes.
Port of FMZ strategy #440368 "基于平滑RSI的股票交易策略Smoothed-RSI-Based-Stock-Trading-Strategy" (Smoothed RSI Strategy).

FMZ source id: 440368

Source
    https://www.fmz.com/strategy/440368 (PineScript v5, FMZ last modified 2024-01-29 16:26:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-143), RSI 5, SMA 5; oversold 40, overbought 80
    smoothedRsi = sma(rsi(close, 5), 5);  crossover(smoothedRsi, 40) -> entry Buy;  crossunder(smoothedRsi, 80) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The two crossings cannot happen on one bar. Long only. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed RSI crossings.
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

NAME = "fmz_440368_smoothed_rsi5_40_80_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [5, 14],
    "oversold": [40, 30],
}
DEFAULT_PARAMS = {"length": 5, "oversold": 40, "overbought": 80}


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
    n = int(p["length"])
    s = _rsi(c, n).rolling(n).mean()
    os_, ob = float(p["oversold"]), float(p["overbought"])
    buy = (s > os_) & (s.shift(1) <= os_)
    sell = (s < ob) & (s.shift(1) >= ob)
    false = pd.Series(False, index=c.index)
    return buy, sell, false, false.copy()


def portfolio_kwargs(**params):
    return {}
