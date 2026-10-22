"""Delta-RSI zero crossings, 4-hour bars: the slope at the last point of a degree-2 least-squares fit to the last 21 values of RSI 21 crossing over zero goes long, crossing under zero goes short; reversing.
Port of FMZ strategy #474681 "动态RSI震荡多项式拟合指标趋势量化交易策略-Dynamic-RSI-Oscillator-Polynomial-Fitting-Indicator-Trend-Quantitative-Trading-Strategy" (D-RSI-Q).

FMZ source id: 474681

Source
    https://www.fmz.com/strategy/474681 (PineScript v5, FMZ last modified 2024-12-11 15:32:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 106-379), polynomial order 2; RSI 21; window 21; signal EMA 9; buy / sell / exit Zero-Crossing; RMSE filter off
    drsi = d/dz of the least-squares polynomial (J[i][j] = i^j, i = 0..20) fitted to rsi[20..0], at z = 20;  crossover(drsi, 0) -> entry long;  crossunder(drsi, 0) -> entry short;  crossunder -> close long;  crossover -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The fit is linear in the window, so the derivative is a fixed weighted sum of the last 21 RSI
      values: weights = d' pinv(J) with d = [0, 1, 2 x 20] (the QR pseudo-inverse of the source equals
      numpy's for this full-rank J). The exits coincide with the opposite entries (all Zero-Crossing),
      so they only repeat the reversals. The signal line and the RMSE filter (off) feed nothing.
      REVERSAL INTENDED. No sizing code. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, polynomial-fit RSI slope crossings.
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

NAME = "fmz_474681_delta_rsi_poly2_slope_zero_cross_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [21, 14],
    "window": [21, 30],
}
DEFAULT_PARAMS = {"rsi_len": 21, "window": 21, "degree": 2}


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


def _drsi(src, window, degree):
    """Slope at the window's last point of the least-squares polynomial (oldest value first)."""
    z = np.arange(window, dtype=float)
    J = np.vander(z, degree + 1, increasing=True)
    d = np.array([j * (window - 1) ** (j - 1) if j >= 1 else 0.0 for j in range(degree + 1)])
    w = d @ np.linalg.pinv(J)
    return src.rolling(window).apply(lambda v: np.dot(w, v), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    r = _rsi(bars_df["close"], int(p["rsi_len"]))
    dr = _drsi(r, int(p["window"]), int(p["degree"]))
    le = (dr > 0) & (dr.shift(1) <= 0)
    se = (dr < 0) & (dr.shift(1) >= 0)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
