"""Hourly Delta-RSI: the slope at the last point of a cubic least-squares fit over the last 50 values of RSI 21; crossing over its EMA 9 signal line goes long, crossing under goes short; reversing.
Port of FMZ strategy #438479 "基于多项式插值的RSI动量指标策略Polynomial-Interpolation-Based-RSI-Momentum-Strategy" (Delta-RSI Strategy with Filters (tbiktag)).

FMZ source id: 438479

Source
    https://www.fmz.com/strategy/438479 (PineScript v4, FMZ last modified 2024-01-12 13:46:53).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 202-549), polynomial order 3; RSI 21; window 50; signal EMA 9; entries and exits on signal-line crossings; all filters off; SL / TP off
    [drsi, nrmse] = diff(rsi(close, 21), 50, 3) (pinv of the Vandermonde matrix i^j, derivative at i = window - 1);  signalline = ema(drsi, 9)
    golong = crossover(drsi, signalline) -> entry long;  goshort = crossunder -> entry short;  endlong = crossunder -> close long;  endshort = drisendlong (sic) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The fit is linear in the window, so D-RSI is a fixed weighted sum of the last 50 RSI values
      (weights from the pseudoinverse; any missing value gives no value). endshort is written as
      drisendlong, so the short close fires on the crossunder that opens a short (weird case); a close
      acts only on a position the bar's entries leave unchanged, so every crossing simply reverses. The
      volume, ATR and RSI filters are off by default: volume is not used. SL / TP are off. REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed RSI derivative against its signal line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438479_delta_rsi_polynomial_slope_signal_cross_1h_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "window": [50, 30],
    "signal_len": [9, 5],
}
DEFAULT_PARAMS = {"degree": 3, "rsi_len": 21, "window": 50, "signal_len": 9}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)
    return r.where(up.notna() & dn.notna())


def _drsi(src, window, degree):
    """Slope at the window's last point of the least-squares polynomial (x = 0 .. window-1)."""
    x = np.arange(window, dtype=float)
    vander = np.vander(x, degree + 1, increasing=True)
    coef_w = np.linalg.pinv(vander)                       # (degree+1, window); column j = value j bars into the window
    w = sum(i * coef_w[i] * (window - 1) ** (i - 1) for i in range(1, degree + 1))
    v = src.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    for t in range(window - 1, len(v)):
        seg = v[t - window + 1:t + 1]                     # oldest first, as Pine's _Y_raw
        if not np.isnan(seg).any():
            out[t] = float(w @ seg)
    return pd.Series(out, index=src.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    degree = int(p["degree"])
    window = max(int(p["window"]), degree + 1)
    d = _drsi(_rsi(c, int(p["rsi_len"])), window, degree)
    sig = d.ewm(span=int(p["signal_len"]), adjust=False).mean()
    up = (d > sig) & (d.shift(1) <= sig.shift(1))
    dn = (d < sig) & (d.shift(1) >= sig.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return up.astype(bool), false, dn.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
