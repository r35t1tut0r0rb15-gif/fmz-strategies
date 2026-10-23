"""Parabolic SAR (0.02 / 0.02 / 0.2) against its own EMA 50 +/- 2.2 standard-deviation band, with SMA 100 +/- ATR 100 Fibonacci levels, 4-hour bars: the previous SAR crossing over the lower band with the SAR under the SMA 100 - 1.618 ATR level goes long, otherwise crossing under the upper band above the shifted SMA + 4.236 ATR level with a falling WMA 10 goes short; reversing.
Port of FMZ strategy #366415 "HIGH LOW SAR" (HIGH LOW SAR).

FMZ source id: 366415

Source
    https://www.fmz.com/strategy/366415 (PineScript v4, FMZ last modified 2022-05-29 10:33:10).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 40-141), len 100; Fibonacci 1.618 / 4.236 x ATR 100; SAR 0.02 / 0.02 / 0.2; band EMA 50 +/- 2.2 stdev of the SAR; "VHMA" (resolves to WMA 10 of the close)
    low1 = crossover(sar[1], ema(sar, 50) - 2.2 stdev(sar, 50)) and sar < sma(close, 100) - 1.618 atr(100) -> entry buy
    high1 = crossunder(sar[1], ema(sar, 50) + 2.2 stdev(sar, 50)) and sar > sma(close[100], 100) + 4.236 atr(100) and vhma < vhma[2] -> entry sell (else)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source's VHMA helper p(src, len) ignores its src argument and averages the close (weights
      (len - i) x len), and its last stage uses len 10: so "vhma" is the WMA 10 of the close and the
      volume-weighted line (ma) feeds nothing; volume is not used, as written. top2 is built on the close
      100 bars back, as written. A study() script sending strategy orders on FMZ; the header is a spot
      pair and the shorts are ported as written (as #428970). REVERSAL INTENDED. No sizing code. The
      source carries the Mozilla Public License 2.0 notice. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SAR band re-entries with ATR / Fibonacci level filters.
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

NAME = "fmz_366415_sar_ema50_band_cross_fib_atr_level_reversal"
FAMILY = "parabolic_sar"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "look_back": [50, 100],
    "multi": [2.2, 1.5],
}
DEFAULT_PARAMS = {"look_back": 50, "multi": 2.2, "length": 100, "start": 0.02, "increment": 0.02, "maximum": 0.2}


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


def _wma(x, n):
    """Pine ta.wma over each n-bar window (NaN when the window holds a NaN)."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.arange(1, n + 1, dtype=float)              # newest bar weighted n
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, n)
    bott1 = c.rolling(n).mean() - atr * 1.618
    top2 = c.shift(n).rolling(n).mean() + atr * 4.236
    vhma = _wma(c, 10)                                 # p(hm, 10): the close, as written
    s1 = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                        float(p["start"]), float(p["increment"]), float(p["maximum"])), index=c.index)
    lb = int(p["look_back"])
    mean = s1.ewm(span=lb, adjust=False).mean()
    dev = float(p["multi"]) * s1.rolling(lb).std(ddof=0)
    b, s2 = mean + dev, mean - dev
    a = s1.shift(1)
    low1 = (a > s2) & (a.shift(1) <= s2.shift(1)) & (s1 < bott1)
    high1 = (a < b) & (a.shift(1) >= b.shift(1)) & (s1 > top2) & (vhma < vhma.shift(2))
    false = pd.Series(False, index=c.index)
    return low1, false, high1 & ~low1, false.copy()


def portfolio_kwargs(**params):
    return {}
