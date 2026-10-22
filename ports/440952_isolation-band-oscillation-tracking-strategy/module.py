"""Chandelier Exit flips, 1-hour bars: the direction turning up (close above the previous short stop, 22-bar extreme close +/- 3 ATR(22)) goes long, turning down short; bar-tested 5 % stop, 20 % target and a
5-point trail after 10 % close the side; reversing.
Port of FMZ strategy #440952 "Isolation Band Oscillation Tracking Strategy" (CE-STG).

FMZ source id: 440952

Source
    https://www.fmz.com/strategy/440952 (PineScript v4, FMZ last modified 2024-02-04 10:28:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 162-238), ATR 22 x 3; close extremes on; long-short on; stop 5 %, target 20 %, trail start 10 %, trail 5 % (ratios of the average price); dates 2019-2025 (window() is true)
    longStop = highest(close, 22) - 3 atr, raised while close[1] > it;  shortStop mirrored;  dir = close > shortStop[1] ? 1 : close < longStop[1] ? -1 : dir;  buySignal = dir turns 1, sellSignal = dir turns -1
    LONG: entry on buySignal; close on sellSignal, (close - avg) / avg < -5 %, (high - avg) / avg > 20 %, or best high ratio[1] > 10 and best[1] - current high ratio > 5;  SHORT mirrored (stop and trail on the close, target on the low)

Interpretation choices (Pine rules in SURVEY_README.md)
    * All exits are bar tests against the fill price, sent at the next open (not orders). The long trail
      tracks the best high ratio and the short trail the best close ratio, as written. The calls run in
      the written order: a close on the signal bar is followed by the opposite entry, so a flip reverses;
      a close acts only on the held position. strategy.entry reverses: REVERSAL INTENDED. The cash size,
      capital and commission are sizing and costs. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bar-tested stop, target and trail.
    2 generic: PASS, Chandelier stops.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: cash size, capital and commission settings.
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

NAME = "fmz_440952_chandelier_flip_ratio_exits"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [22, 14],
    "mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"length": 22, "mult": 3.0, "sl": 5.0, "tp": 20.0, "ts_start": 10.0, "ts": 5.0}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def _direction(bars_df, n, k):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    a = (k * _rma(tr, n)).to_numpy()
    hc, lc = c.rolling(n).max().to_numpy(), c.rolling(n).min().to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    d = np.ones(m, dtype=np.int8)
    ls_p = ss_p = np.nan
    dv = 1
    for i in range(m):
        ls, ss = hc[i] - a[i], lc[i] + a[i]
        lsp = ls if np.isnan(ls_p) else ls_p
        ssp = ss if np.isnan(ss_p) else ss_p
        if i > 0 and cv[i - 1] > lsp and not np.isnan(ls):
            ls = max(ls, lsp)
        if i > 0 and cv[i - 1] < ssp and not np.isnan(ss):
            ss = min(ss, ssp)
        if cv[i] > ssp:
            dv = 1
        elif cv[i] < lsp:
            dv = -1
        d[i] = dv
        ls_p, ss_p = ls, ss
    return d


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    d = _direction(bars_df, int(p["length"]), float(p["mult"]))
    prev_d = np.concatenate(([1], d[:-1]))
    buy, sell = (d == 1) & (prev_d == -1), (d == -1) & (prev_d == 1)
    ov, hv, lv, cv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    sl, tp, tss, ts = (float(p[k]) for k in ("sl", "tp", "ts_start", "ts"))
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, x = 0, np.nan
    best_l = best_s = 0.0
    for i in range(m):
        hi_r = (hv[i] - x) / x * 100 if pos == 1 else np.nan
        lo_r = (cv[i] - x) / x * 100 if pos != 0 else np.nan
        s_hi = (lv[i] - x) / x * 100 if pos == -1 else np.nan
        bl_prev, bs_prev = best_l, best_s
        best_l = (hi_r if hi_r > best_l else best_l) if pos == 1 else 0.0
        best_s = (lo_r if lo_r < best_s else best_s) if pos == -1 else 0.0
        new = pos
        if buy[i]:
            new = 1
        if pos == 1 and new == 1 and (sell[i] or lo_r < -sl or hi_r > tp or (bl_prev > tss and bl_prev - hi_r > ts)):
            new = 0
        if sell[i]:
            new = -1
        if pos == -1 and new == -1 and (buy[i] or lo_r > sl or s_hi < -tp or (-bs_prev > tss and -(bs_prev - lo_r) > ts)):
            new = 0
        if new != 0 and new != pos and i + 1 < m:
            x = ov[i + 1]                                # the fill of the new position
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
