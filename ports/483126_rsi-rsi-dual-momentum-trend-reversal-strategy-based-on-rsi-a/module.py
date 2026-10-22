"""RSI 14 extremes with Stochastic RSI 14 / 3 / 3 K-D crossings, hourly bars: RSI under 30 with %K under 20 crossing over %D goes long, RSI over 70 with %K over 80 crossing under %D goes short; RSI past the other extreme or the opposite K-D cross closes; reversing.
Port of FMZ strategy #483126 "基于RSI和随机RSI的双重动量趋势反转策略-Dual-Momentum-Trend-Reversal-Strategy-Based-on-RSI-and-Stochastic-RSI" (RSI + Stochastic RSI Strategy).

FMZ source id: 483126

Source
    https://www.fmz.com/strategy/483126 (PineScript v5, FMZ last modified 2025-02-27 16:53:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-159), RSI 14 / 70 / 30; Stochastic RSI 14, K 3, D 3, levels 80 / 20; 10 % of equity, capital 100000
    rsi < 30 and k < 20 and crossover(k, d) -> entry Long;  rsi > 70 or crossunder(k, d) -> close Long
    rsi > 70 and k > 80 and crossunder(k, d) -> entry Short;  rsi < 30 or crossover(k, d) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A close on the bar of an entry is masked by the entry; an entry on the other side reverses
      (REVERSAL INTENDED). The 10 % of equity size and the capital are sizing. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI extremes with Stochastic RSI crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity and capital stored, not ported.
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

NAME = "fmz_483126_rsi14_extreme_stochrsi_kd_cross_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [14, 7],
    "stoch_length": [14, 9],
}
DEFAULT_PARAMS = {"rsi_length": 14, "stoch_length": 14, "smooth_k": 3, "smooth_d": 3}


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    n = int(p["stoch_length"])
    rr = r.rolling(n).max() - r.rolling(n).min()
    k = (100 * (r - r.rolling(n).min()) / rr.where(rr > 0)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    ku = (k > d) & (k.shift(1) <= d.shift(1))
    kd = (k < d) & (k.shift(1) >= d.shift(1))
    le = (r < 30) & (k < 20) & ku
    se = (r > 70) & (k > 80) & kd
    lx = (r > 70) | kd
    sx = (r < 30) | ku
    return le, lx & ~le & ~se, se, sx & ~se & ~le


def portfolio_kwargs(**params):
    return {}
