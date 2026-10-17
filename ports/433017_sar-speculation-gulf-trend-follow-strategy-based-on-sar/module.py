"""Parabolic SAR flips with three filters, 1-hour bars, long only: within 4 bars of the close crossing above the SAR, with
the close above the SAR and the EMA 100, a candle body larger than the 100-bar stdev of bodies, and a rising squeeze
momentum line, a long opens; a close under the SAR closes it.
Port of FMZ strategy #433017 "基于-SAR-的趋势追踪型量化策略Speculation-Gulf-Trend-Follow-Strategy-Based-on-SAR" (BT-SAR Ema, Squeeze, Voltatility (SAR ESV)).

FMZ source id: 433017

Source
    https://www.fmz.com/strategy/433017 (PineScript v5, FMZ last modified 2023-11-23 16:26:17).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 203-372), SAR 0.02 / 0.02 / 0.2, signal "SAR Flip", bars 4; EMA 100 on; volatility 100 on; squeeze (KC 20 / 1.5) on; exit "SAR Flip"; trailing off
    check = close[1] < sar[1] and close > sar;  openLong = close > sar and close > ema100 and (close - open) > stdev(close - open, 100) and val > val[1] and barssince(check) < 4
    val = linreg(close - avg(avg(highest(high, 20), lowest(low, 20)), sma(close, 20)), 20, 0)
    openLong -> entry long;  close < sar -> close long (tpType "SAR Flip": the exit's limit and stop are na)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.sar as TradingView documents it (the same helper as #431693). Pine's stdev is the population
      stdev; linreg(x, 20, 0) is the least-squares line read at the last bar.
    * The squeeze on / off flags are computed but not used by the default filter (val > val[1] only).
      The Fixed % and Risk Reward exits and the trailing take profit are off by default.
    * Long only; Opposite entries cannot occur. The date window is always true. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SAR position, averages, body stdev and a momentum slope.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (the bot alert messages are not trading rules).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433017_sar_flip_ema_squeeze"
FAMILY = "parabolic_sar"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [100, 200],
    "n_bars": [4, 8],
}
DEFAULT_PARAMS = {"sar_start": 0.02, "sar_inc": 0.02, "sar_max": 0.2, "n_bars": 4, "ema_len": 100,
                  "vol_len": 100, "kc_len": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _sar_pine(bars, start, inc, maximum):
    """ta.sar as TradingView documents it (pine_sar): starts on bar 1, direction from close vs
    the previous close; value capped by the previous two bars' lows (highs)."""
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    out = np.full(m, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, m):
        first = False
        if i == 1:
            if c[1] > c[0]:
                below, max_min, result = True, h[1], lo[0]
            else:
                below, max_min, result = False, lo[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if below:
            if result > lo[i]:
                first, below = True, False
                result, max_min, acc = max(h[i], max_min), lo[i], start
        else:
            if result < h[i]:
                first, below = True, True
                result, max_min, acc = min(lo[i], max_min), h[i], start
        if not first:
            if below and h[i] > max_min:
                max_min, acc = h[i], min(acc + inc, maximum)
            elif (not below) and lo[i] < max_min:
                max_min, acc = lo[i], min(acc + inc, maximum)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return pd.Series(out, index=bars.index)


def _linreg(x, n):
    """Pine linreg(x, n, 0): the least-squares line through the last n values, read at the last."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        win = np.lib.stride_tricks.sliding_window_view(v, n)
        t = np.arange(n, dtype=float) - (n - 1) / 2.0
        slope = win @ t / float(t @ t)
        out[n - 1:] = win.mean(axis=1) + slope * (n - 1) / 2.0
    return pd.Series(out, index=x.index)


def _barssince(cond):
    v = cond.to_numpy()
    out = np.full(len(v), np.nan)
    last = -1
    for i in range(len(v)):
        if v[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    sar = _sar_pine(bars_df, float(p["sar_start"]), float(p["sar_inc"]), float(p["sar_max"]))
    check = (c.shift(1) < sar.shift(1)) & (c > sar)
    since = _barssince(check)
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    spike = c - o
    vol_ok = spike > spike.rolling(int(p["vol_len"])).std(ddof=0)
    k = int(p["kc_len"])
    mid = ((h.rolling(k).max() + lo.rolling(k).min()) / 2 + c.rolling(k).mean()) / 2
    val = _linreg(c - mid, k)
    with np.errstate(invalid="ignore"):
        ent = ((c > sar) & (c > ema) & vol_ok & (val > val.shift(1))).to_numpy() & (since < int(p["n_bars"]))
    ex = (c < sar).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 0 and ent[i]:
            pos = 1
        elif pos == 1 and ex[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev == 0), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
