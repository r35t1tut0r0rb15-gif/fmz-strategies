"""RSI 14 crossings of 30 / 70 with ADX 14 over 25 and a 20-bar least-squares line fitted value, hourly bars: RSI up through 30 with the fitted value over the close goes long, RSI down through 70 with it under the close goes short; reversing, no other exit.
Port of FMZ strategy #483106 "趋势增强型RSI-ADX线性回归预测交易策略-Enhanced-Trend-RSI-ADX-Linear-Regression-Prediction-Trading-Strategy" (RSI + ADX + ML-like Strategy (5min)).

FMZ source id: 483106

Source
    https://www.fmz.com/strategy/483106 (PineScript v5, FMZ last modified 2025-02-21 13:46:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-140), RSI 14; DMI / ADX 14; regression lookback 20
    predictedClose = slope x bar_index + intercept, the least-squares line of close on bar_index over 20 bars, at the current bar
    crossover(rsi, 30) and adx > 25 and predictedClose > close -> entry Long;  crossunder(rsi, 70) and adx > 25 and predictedClose < close -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The fitted value does not depend on where bar_index starts, so the module's own bar positions are
      used. ta.dmi is Wilder's DMI. The title's 5 minutes is not the header's bar size (1h). Entries only:
      each reverses the other side (REVERSAL INTENDED), no other exit. No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI level crossings with ADX and a regression filter.
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

NAME = "fmz_483106_rsi14_30_70_cross_adx25_linreg20_side_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [14, 7],
    "ml_lookback": [20, 50],
}
DEFAULT_PARAMS = {"rsi_length": 14, "ml_lookback": 20, "adx_length": 14, "adx_min": 25.0}


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


def _adx(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0)
    mdm = dn.where((dn > up) & (dn > 0), 0.0)
    trs = _rma(tr, n)
    pdi, mdi = 100 * _rma(pdm, n) / trs, 100 * _rma(mdm, n) / trs
    s = pdi + mdi
    return _rma(100 * (pdi - mdi).abs() / s.where(s > 0), n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["ml_lookback"])
    x = pd.Series(np.arange(len(c), dtype=float), index=c.index)
    sx, sy = x.rolling(n).sum(), c.rolling(n).sum()
    sxy, sx2 = (x * c).rolling(n).sum(), (x * x).rolling(n).sum()
    slope = (n * sxy - sx * sy) / (n * sx2 - sx * sx)
    pred = slope * x + (sy - slope * sx) / n
    r = _rsi(c, int(p["rsi_length"]))
    trend = _adx(bars_df, int(p["adx_length"])) > float(p["adx_min"])
    le = (r > 30) & (r.shift(1) <= 30) & trend & (pred > c)
    se = (r < 70) & (r.shift(1) >= 70) & trend & (pred < c)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
