"""Hourly bars: CCI 5 under -75 with the low under the lower Keltner line (SMA 30 of hlc3 - 0.7 x ATR 30) and RSI 30 under 60 goes long; CCI over 75 with the high over the upper line and RSI over 60 goes short; CCI back over 0 closes a long, under 0 a short; reversing.
Port of FMZ strategy #442944 "基于肯特纳通道和CCI指标的趋势过滤量化策略Trend-Filter-Quantitative-Strategy-Based-on-Keltner-Channels-and-CCI-Indicator" (Custom Keltner CCI Strategy with Trend Filter).

FMZ source id: 442944

Source
    https://www.fmz.com/strategy/442944 (PineScript v4, FMZ last modified 2024-02-27 15:47:20).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 168-224), trend filter OFF; KC 30 x 0.7; CCI 5, 75 / -75; RSI 30, 60 / 60; volume multiplier 0
    longCondition = cci < -75 and low < lowerChannel and rsi < 60 and volume > sma(volume, 50) x 0 -> entry Long
    shortCondition = cci > 75 and high > upperChannel and rsi > 60 and volCondition -> entry Short;  close Long when cci > 0;  close Short when cci < 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the volume multiplier at 0 the volume test is only volume > 0 (kept). The trend filter is
      OFF. A close acts only on a position the bar's entries leave unchanged. REVERSAL INTENDED. No sizing
      code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Keltner-band extremes confirmed by CCI and RSI, CCI zero-line exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) only as volume > 0 x its SMA 50 (any bar with volume); exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442944_keltner_cci5_rsi30_extremes_zero_exit_1h_reversal"
FAMILY = "keltner_channel"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "kc_mult": [0.7, 1.5],
    "cci_len": [5, 14],
}
DEFAULT_PARAMS = {"kc_len": 30, "kc_mult": 0.7, "cci_len": 5, "cci_ob": 75.0, "cci_os": -75.0, "rsi_len": 30,
                  "rsi_ob": 60.0, "rsi_os": 60.0, "vol_mult": 0.0}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _cci(x, n):
    sma = x.rolling(n).mean()
    mad = pd.Series(np.nan, index=x.index)
    if len(x) >= n:
        win = np.lib.stride_tricks.sliding_window_view(x.to_numpy(dtype=float), n)
        mad.iloc[n - 1:] = np.abs(win - win.mean(axis=1, keepdims=True)).mean(axis=1)
    return (x - sma) / (0.015 * mad).where(mad != 0)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["kc_len"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    mid = ((h + lo + c) / 3).rolling(n).mean()
    rng = float(p["kc_mult"]) * _rma(tr, n)
    upper, lower = mid + rng, mid - rng
    cci = _cci(c, int(p["cci_len"]))
    rsi = _rsi(c, int(p["rsi_len"]))
    vol_ok = v > v.rolling(50).mean() * float(p["vol_mult"])
    lg = ((cci < float(p["cci_os"])) & (lo < lower) & (rsi < float(p["rsi_os"])) & vol_ok).to_numpy()
    sh = ((cci > float(p["cci_ob"])) & (h > upper) & (rsi > float(p["rsi_ob"])) & vol_ok).to_numpy()
    xl, xs = (cci > 0).to_numpy(), (cci < 0).to_numpy()
    m = len(lg)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if lg[i] and new != 1:
            new = 1
        if sh[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and xl[i]:
                new = 0
            elif pos == -1 and xs[i]:
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
