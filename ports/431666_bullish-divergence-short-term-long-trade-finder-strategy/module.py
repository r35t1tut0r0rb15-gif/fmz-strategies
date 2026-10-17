"""RSI bullish divergences, 1-minute bars, long only: a confirmed RSI 14 pivot low (25 bars left, 5 right) with a higher RSI
than the previous qualifying pivot, a lower low than the previous pivot's bar, the close under that low and the last
completed hour's RSI under 40 goes long; a close 5 % under the entry, RSI over 75 or a bearish divergence closes it.
Port of FMZ strategy #431666 "Bullish Divergence Short term Long Trade Finder Strategy" (Bullish Divergence Short-term Long Trade Finder).

FMZ source id: 431666

Source
    https://www.fmz.com/strategy/431666 (PineScript v5, FMZ last modified 2023-11-10 11:37:37).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 207-286), RSI 14, pivots 25 / 5, range 5-50, bull < 40, bear > 50 / 60, sell 75, stop 5 %
    pivot_low_true = pivotlow(rsi, 25, 5) found on this bar;  RSI_HL_check = rsi < 40 and rsi > valuewhen(pivot_low_true and rsi < 40, rsi, 1)
      and 5 <= barssince(pivot_low_true[1]) <= 50;  price_ll_check = low < valuewhen(pivot_low_true, low, 1)
    bullCond = price_ll_check and RSI_HL_check and pivot_low_true;  bearCond mirrored on pivot highs with rsi[3] > 60
    bullCond and close < valuewhen(pivot_low_true, low, 1) and security('60', rsi) < 40 -> entry long
    long and close < avg x 0.95 -> close;  long and (rsi > 75 or bearCond) -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written, the checks read rsi and low on the confirmation bar (5 bars after the pivot), not
      at the pivot. Pivots are strict (as #430840). confirm_range(x) is barssince(x) between 5 and 50.
    * security('60', rsi) without lookahead on the 1-minute chart is read as the last completed
      hour's RSI 14 (hours on the UTC clock, built inside simulate() from the port's own bars). The
      4-hour and daily RSIs are unused.
    * The 5 % stop is close-checked from the entry fill (the open after the signal). The closes act on
      the position held at the bar's start. Long only; Opposite entries cannot occur. FREQ = "1min"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked exits.
    2 generic: PASS, RSI pivots, price lows and a percentage stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_431666_rsi_bull_divergence_long"
FAMILY = "macd_divergence"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pivot_left": [25, 10],
    "stop_pct": [5, 2],
}
DEFAULT_PARAMS = {"pivot_left": 25, "pivot_right": 5, "stop_pct": 5, "rsi_len": 14, "bull_min": 40,
                  "bear_min": 50, "bear_sell_min": 60, "sell_rsi": 75}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _pivots(x, lb, rb, high):
    """True at bar t when bar t - rb is a strict pivot over lb bars before and rb bars after."""
    m = len(x)
    out = np.zeros(m, dtype=bool)
    for t in range(lb + rb, m):
        j = t - rb
        v = x[j]
        left, right = x[j - lb:j], x[j + 1:t + 1]
        if high:
            out[t] = v > left.max() and v > right.max()
        else:
            out[t] = v < left.min() and v < right.min()
    return out


def _vw1(cond, x):
    """valuewhen(cond, x, 1): x at the second most recent bar where cond held (this bar included)."""
    m = len(x)
    out = np.full(m, np.nan)
    a = b = np.nan
    for t in range(m):
        if cond[t]:
            a, b = x[t], a
        out[t] = b
    return out


def _in_range(cond, lo_, hi_):
    """lo_ <= barssince(cond) <= hi_."""
    m = len(cond)
    out = np.zeros(m, dtype=bool)
    last = -1
    for t in range(m):
        if cond[t]:
            last = t
        out[t] = last >= 0 and lo_ <= t - last <= hi_
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["rsi_len"])
    r = _rsi(c, n).to_numpy()
    hour = bars_df.index.floor("h")
    hc = c.groupby(hour).last()
    rh = _rsi(hc, n).shift(1)                                   # the last completed hour
    r_hour = rh.reindex(hour).to_numpy()
    lb, rb = int(p["pivot_left"]), int(p["pivot_right"])
    pl, ph = _pivots(r, lb, rb, False), _pivots(r, lb, rb, True)
    lv, hv, cv, ov = (x.to_numpy(dtype=float) for x in (lo, h, c, o))
    m = len(cv)
    pl1 = np.concatenate(([False], pl[:-1]))
    ph1 = np.concatenate(([False], ph[:-1]))
    bull_min = float(p["bull_min"])
    hl = (r < bull_min) & (r > _vw1(pl & (r < bull_min), r)) & _in_range(pl1, 5, 50)
    prev_low = _vw1(pl, lv)
    bull = (lv < prev_low) & hl & pl
    lh = (r < _vw1(ph & (r > float(p["bear_min"])), r)) & _in_range(ph1, 5, 50)
    r3 = np.concatenate(([np.nan] * 3, r[:-3])) if m > 3 else np.full(m, np.nan)
    bear = (hv > _vw1(ph, hv)) & lh & ph & (r3 > float(p["bear_sell_min"]))
    entry = bull & (cv < prev_low) & (r_hour < 40)
    k = 1 - float(p["stop_pct"]) / 100
    tgt = np.zeros(m, dtype=np.int8)
    pos, avg = 0, np.nan
    for i in range(m):
        start = pos
        if entry[i] and pos == 0:
            pos = 1
            if i + 1 < m:
                avg = ov[i + 1]
        if start == 1 and (cv[i] < avg * k or r[i] > float(p["sell_rsi"]) or bear[i]):
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
