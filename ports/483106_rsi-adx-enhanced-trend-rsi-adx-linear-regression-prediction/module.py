"""RSI 14 leaving oversold (overbought) while ADX 14 is above 25 and the 20-bar regression line is above (below) the
close, always in the market, 1-hour bars: RSI crossing above 30 with ADX > 25 and the regression value above the close
goes long; RSI crossing below 70 with ADX > 25 and the regression value below the close goes short.
Port of FMZ strategy #483106 "趋势增强型RSI-ADX线性回归预测交易策略-Enhanced-Trend-RSI-ADX-Linear-Regression-Prediction-Trading-Strategy" (RSI + ADX + ML-like Strategy (5min)).

FMZ source id: 483106

Source
    https://www.fmz.com/strategy/483106 (PineScript v5, FMZ last modified 2025-02-21 13:46:54).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 104-135), RSI 14, DMI 14 / 14, lookback 20
    predicted = least-squares line of close on bar_index over the last 20 bars, at this bar
    long = crossover(rsi, 30) and adx > 25 and predicted > close; short = crossunder(rsi, 70) and adx > 25 and
    predicted < close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "ML" value is the 20-bar linear regression of the close evaluated at the current bar (ta.linreg(close, 20,
      0)); computed on each window with centred x for numerical accuracy (the same line).
    * ADX as Pine's ta.dmi (as #426579). Entries reverse (REVERSAL INTENDED); no exits, no stops. "5min" in the title
      is a label: FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI, ADX and a rolling regression.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
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

NAME = "fmz_483106_rsi_exit_extreme_adx_linreg_reversal"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_min": [25.0, 20.0],
    "lookback": [20, 50],
}
DEFAULT_PARAMS = {"rsi_len": 14, "adx_len": 14, "adx_min": 25.0, "lookback": 20}


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
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _fixnan(v):
    """Pine fixnan: replace na by the last non-na value (past values only)."""
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1]
    return out


def _adx_pine(bars, di_len, adx_len):
    """Pine's built-in-style dirmov/adx: RMA smoothing, fixnan on DI+/DI-."""
    h, lo, c = bars["high"], bars["low"], bars["close"]
    up, down = h.diff(), -lo.diff()
    plus_dm = np.where(up.isna(), np.nan, np.where((up > down) & (up > 0), up, 0.0))
    minus_dm = np.where(down.isna(), np.nan, np.where((down > up) & (down > 0), down, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    trs = _rma(tr, di_len)
    plus = _fixnan((100 * _rma(pd.Series(plus_dm, index=h.index), di_len) / trs).to_numpy())
    minus = _fixnan((100 * _rma(pd.Series(minus_dm, index=h.index), di_len) / trs).to_numpy())
    s = plus + minus
    dx = pd.Series(np.abs(plus - minus) / np.where(s == 0, 1, s), index=h.index)
    return pd.Series(plus, index=h.index), pd.Series(minus, index=h.index), 100 * _rma(dx, adx_len)


def _linreg_last(c, n):
    """Least-squares line over the last n values, evaluated at the last one (ta.linreg(src, n, 0))."""
    v = c.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.lib.stride_tricks.sliding_window_view(v, n)
        x = np.arange(n) - (n - 1) / 2
        wm = w.mean(axis=1)
        slope = ((w - wm[:, None]) * x).sum(axis=1) / (x * x).sum()
        out[n - 1:] = wm + slope * (n - 1) / 2
    return pd.Series(out, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"]))
    _, _, adx = _adx_pine(bars_df, int(p["adx_len"]), int(p["adx_len"]))
    pred = _linreg_last(c, int(p["lookback"]))
    strong = adx > p["adx_min"]
    long_e = ((rsi > 30) & (rsi.shift(1) <= 30) & strong & (pred > c)).astype(bool)
    short_e = ((rsi < 70) & (rsi.shift(1) >= 70) & strong & (pred < c)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
