"""Nadaraya-Watson (rational-quadratic kernel, 61 bars) envelope of 2.7 ATR(32), 1-hour bars: the low under the lower band goes long; three closes in a row under the fill price close the long; the high
over the upper band closes the long and goes short.
Port of FMZ strategy #442511 "基于Nadaraya-Watson回归和ATR通道的趋势跟踪策略Trend-Following-Strategy-Based-on-Nadaraya-Watson-Regression-and-ATR-Channel" (Custom Strategy with Stop Loss and EMA).

FMZ source id: 442511

Source
    https://www.fmz.com/strategy/442511 (PineScript v5, FMZ last modified 2024-02-22 15:15:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 122-181), source close; lookback 10, weighting 10, regression start 50, lag 2 (second estimate unused); stop bars 3; EMA 46 (plots only); ATR 32 x 2.7
    yhat1 = sum(close[i] w(i)) / sum(w(i)), i = 0 .. h + x_0, w(i) = (1 + i^2 / (2 r h^2))^-r;  upper / lower = yhat1 +- 2.7 atr(32)
    low < lower -> entry Long;  close[1], close[2], close[3] < position_avg_price -> close Long;  high > upper -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The kernel sum runs over the current bar and the 60 before it (h + x_0 = 60), so the estimate
      exists from the 61st bar. The stop rule compares the three previous closes with the average
      (fill) price, as written, from the bar the long is held at (strategy.close of "Long" does nothing
      while short or flat). The short has no exit but the next long entry's reversal. The second
      estimate and the EMAs only plot. Entries in call order with one position at a time. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, kernel-regression ATR envelope; closes against the fill price.
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

NAME = "fmz_442511_nadaraya_watson_atr_envelope_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "coef": [2.7, 2.0],
    "atr_len": [32, 14],
}
DEFAULT_PARAMS = {"coef": 2.7, "atr_len": 32, "h": 10, "r": 10.0, "x_0": 50, "stop_bars": 3}


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


def _kernel(src, size, hh, r, x0):
    k = np.arange(size + x0 + 1, dtype=float)
    w = (1.0 + k ** 2 / (hh ** 2 * 2 * r)) ** (-r)
    num = sum(src.shift(int(j)) * w[j] for j in range(len(w)))
    return num / w.sum()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    hh = int(p["h"])
    yhat = _kernel(c, hh, hh, float(p["r"]), int(p["x_0"]))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_len"]))
    up, dn = yhat + float(p["coef"]) * atr, yhat - float(p["coef"]) * atr
    lc = (lo < dn).to_numpy()
    sc = (h > up).to_numpy()
    cv, ov = c.to_numpy(dtype=float), o.to_numpy(dtype=float)
    nb = int(p["stop_bars"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    held, fill = 0, np.nan
    for i in range(m):
        new = held
        if lc[i] and new != 1:
            new = 1
        if held == 1 and new == 1 and i >= nb and all(cv[i - k] < fill for k in range(1, nb + 1)):
            new = 0
        if sc[i] and held == 1 and new == 1:
            new = 0
        if sc[i] and new != -1:
            new = -1
        tgt[i] = new
        if new != held and new != 0 and i + 1 < m:
            fill = ov[i + 1]
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
