"""Close crossings of the Parabolic SAR 0.02 / 0.02 / 0.2, 3-hour bars, filtered by RSI 14, MACD side, Stochastic RSI 14 and the close against the LSMA 4 of nine bars back: the up-cross goes long, the down-cross goes short; reversing.
Port of FMZ strategy #488527 "多指标联动SAR反转策略与过滤入场模型-Multi-Indicator-Synergistic-SAR-Reversal-Strategy-with-Filtered-Entry-Model" (SAR Reversal Strategy with Filtered Entries & Opposite Exits).

FMZ source id: 488527

Source
    https://www.fmz.com/strategy/488527 (PineScript v6, FMZ last modified 2025-03-28 16:36:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 170-242), SAR 0.02 / 0.02 / 0.2; RSI 14 / 70 / 30; Stoch RSI 14 / 80 / 20; LSMA 4, offset 9; MACD 12 / 26 / 9; 10 % of equity
    crossover(close, sar) and rsi > 30 and macd > signal and stoch(rsi, 14) > 20 and close > linreg(close, 4, 0)[9] -> close Short, entry Long
    crossunder(close, sar) and rsi < 70 and macd < signal and stoch(rsi, 14) < 80 and close < linreg(close, 4, 0)[9] -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Stochastic of RSI uses RSI as its high, low and close (na when the 14-bar range is zero). The
      LSMA is the 4-bar least-squares line at its last point, taken nine bars back. Each signal closes the
      other side and enters: REVERSAL INTENDED. ta.sar follows Pine's reference implementation. FREQ =
      "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SAR crossings with RSI / MACD / Stochastic RSI / LSMA filters.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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
from numpy.lib.stride_tricks import sliding_window_view

NAME = "fmz_488527_psar_cross_rsi_macd_stochrsi_lsma_filter_reversal"
FAMILY = "parabolic_sar"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lsmaOffset": [9, 0],
    "stochLength": [14, 7],
}
DEFAULT_PARAMS = {"lsmaOffset": 9, "stochLength": 14, "lsmaLength": 4, "start": 0.02, "increment": 0.02,
                  "maximum": 0.2, "rsiPeriod": 14}


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


def _sar(hv, lv, cv, start, inc, mx):
    """Pine's ta.sar as documented (pine_sar)."""
    m = len(cv)
    out = np.full(m, np.nan)
    res = mm = acc = np.nan
    below = None
    for i in range(1, m):
        first = False
        if i == 1:
            if cv[1] > cv[0]:
                below, mm, res = True, hv[1], lv[0]
            else:
                below, mm, res = False, lv[1], hv[0]
            first, acc = True, start
        res = res + acc * (mm - res)
        if below:
            if res > lv[i]:
                first, below = True, False
                res, mm, acc = max(hv[i], mm), lv[i], start
        else:
            if res < hv[i]:
                first, below = True, True
                res, mm, acc = min(lv[i], mm), hv[i], start
        if not first:
            if below:
                if hv[i] > mm:
                    mm, acc = hv[i], min(acc + inc, mx)
            else:
                if lv[i] < mm:
                    mm, acc = lv[i], min(acc + inc, mx)
        if below:
            res = min(res, lv[i - 1])
            if i > 1:
                res = min(res, lv[i - 2])
        else:
            res = max(res, hv[i - 1])
            if i > 1:
                res = max(res, hv[i - 2])
        out[i] = res
    return out


def _linreg(c, n):
    """ta.linreg(c, n, 0): the n-bar least-squares line's value at the newest bar."""
    v = c.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        x = np.arange(n, dtype=float)
        xm = x.mean()
        w = 1.0 / n + (x - xm) * (n - 1 - xm) / ((x - xm) ** 2).sum()
        out[n - 1:] = sliding_window_view(v, n) @ w
    return pd.Series(out, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    sar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                         float(p["start"]), float(p["increment"]), float(p["maximum"])), index=c.index)
    r = _rsi(c, int(p["rsiPeriod"]))
    k = int(p["stochLength"])
    rlo, rhi = r.rolling(k).min(), r.rolling(k).max()
    st = 100 * (r - rlo) / (rhi - rlo).where(rhi > rlo)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    ls = _linreg(c, int(p["lsmaLength"])).shift(int(p["lsmaOffset"]))
    up = (c > sar) & (c.shift(1) <= sar.shift(1))
    dn = (c < sar) & (c.shift(1) >= sar.shift(1))
    le = up & (r > 30) & (macd > sig) & (st > 20) & (c > ls)
    se = dn & (r < 70) & (macd < sig) & (st < 80) & (c < ls)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
