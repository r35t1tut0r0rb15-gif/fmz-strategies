"""Smoothed RSI-gap crossings, 1-hour bars, long only: the 13-bar SMA of (RSI 3 minus its 21-bar SMA) crossing above zero goes long, crossing below closes.
Port of FMZ strategy #440720 "Momentum Indicator Crossover Strategy" (RSI&SMA).

FMZ source id: 440720

Source
    https://www.fmz.com/strategy/440720 (PineScript v4, FMZ last modified 2024-02-01 14:50:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 123-154), RSI 3; SMA 21 of the RSI; SMA 13 of the gap; threshold 0; trend filter off; start 2017
    delta = rsi3 - sma(rsi3, 21);  s2 = sma(delta, 13);  crossover(s2, 0) -> entry BUY;  crossunder(s2, 0) -> close BUY

Interpretation choices (Pine rules in SURVEY_README.md)
    * The EMA 200 filter is off by default. The start date is dropped. Long only. No sizing code. FREQ
      = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed RSI gap.
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

NAME = "fmz_440720_rsi3_gap_sma_zero_cross_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [3, 7],
    "length3": [13, 21],
}
DEFAULT_PARAMS = {"length": 3, "length3": 13, "length2": 21, "threshold": 0.0}


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
    r = _rsi(c, int(p["length"]))
    s2 = (r - r.rolling(int(p["length2"])).mean()).rolling(int(p["length3"])).mean()
    t = float(p["threshold"])
    buy = (s2 > t) & (s2.shift(1) <= t)
    sell = (s2 < t) & (s2.shift(1) >= t)
    false = pd.Series(False, index=c.index)
    return buy, sell, false, false.copy()


def portfolio_kwargs(**params):
    return {}
