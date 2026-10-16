"""Stochastic against RSI-of-ATR bands, hourly bars: the smoothed stochastic crossing above the upper band
(100 - RSI(ATR) - 10) goes long, crossing below the lower band (RSI(ATR) + 10) goes short, unless the
same bar also crosses the other way (skip).
Port of FMZ strategy #428794 "动态止损随ATR波动自适应的动量敲入策略Dynamic-Stop-Loss-Strategy-Adaptive-to-ATR-Fluctuations" (Stoch + ATR).

FMZ source id: 428794

Source
    https://www.fmz.com/strategy/428794 (PineScript v3, FMZ last modified 2023-10-09 15:30:29).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 157-198), stochastic 34 smoothed 2, ATR 34, RSI(ATR) 34, offset 10
    low = rsi(atr(34), 34) + 10; up = 100 - rsi(atr(34), 34) - 10
    belowLine = crossover(k, up) -> entry long; aboveLine = crossunder(k, low) -> entry short
    skip = (crossover(k, low) or crossunder(k, up)) and (aboveLine or belowLine) -> strategy.cancel_all()

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.cancel_all() on a skip bar cancels that bar's unfilled entry orders: no entry on a
      skip bar. stoch(close, high, low, 34) = 100 x (close - lowest low) / (highest high - lowest
      low), current bar included; rsi() of the ATR series is Wilder's.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels only (the ATR enters through its RSI).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and commission stored.
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

NAME = "fmz_428794_stoch_vs_rsi_of_atr"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [34, 14],
    "offset": [10, 0],
}
DEFAULT_PARAMS = {"length": 34, "smooth_k": 2, "offset": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["smooth_k"])).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    ra = _rsi(_rma(tr, n), n)
    low_l = ra + p["offset"]
    up_l = 100 - ra - p["offset"]
    xo = lambda a, b: (a > b) & (a.shift(1) <= b.shift(1))  # noqa: E731
    above = xo(low_l, k)          # crossunder(k, low)
    below = xo(k, up_l)           # crossover(k, up)
    above2 = xo(k, low_l)         # crossover(k, low)
    below2 = xo(up_l, k)          # crossunder(k, up)
    skip = (above2 | below2) & (above | below)
    long_e = (below & ~skip).astype(bool)
    short_e = (above & ~skip).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
