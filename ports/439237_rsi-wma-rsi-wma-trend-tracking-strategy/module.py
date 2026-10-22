"""Smoothed RSI 2 dips with a WMA exit, long only, 5-minute bars: a WMA(2) of the RSI 2 crossing under 10 goes long; the close crossing over its WMA 50 closes.
Port of FMZ strategy #439237 "基于RSI和WMA的趋势追踪策略RSI-WMA-Trend-Tracking-Strategy" (RSI/WMA Strategy).

FMZ source id: 439237

Source
    https://www.fmz.com/strategy/439237 (PineScript v5, FMZ last modified 2024-01-18 15:35:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 171-206), RSI length 2, oversold 10, overbought 90; WMA 50; long trades and long exit on, short trades and short exit off
    vrsi = wma(rsi(close, 2), 2);  co = crossunder(vrsi, 10);  if not na(vrsi) and co: entry RsiLE
    if crossover(close, wma(close, 50)): close RsiLE

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry and the close act on the position held at the bar close: from flat the entry opens (the
      close has nothing to close); a long meeting both closes. The short side is off by default. Long
      only. No sizing code. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI and WMA crossings.
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

NAME = "fmz_439237_wma_rsi2_dip_wma50_exit_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [2, 3],
    "wma_length": [50, 100],
}
DEFAULT_PARAMS = {"length": 2, "wma_length": 50, "oversold": 10}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    v = _wma(_rsi(c, int(p["length"])), 2)
    lvl = float(p["oversold"])
    co = ((v < lvl) & (v.shift(1) >= lvl)).to_numpy()
    w = _wma(c, int(p["wma_length"]))
    xo = ((c > w) & (c.shift(1) <= w.shift(1))).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and xo[i]:
            lx[i], pos = True, 0
        elif pos == 0 and co[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
