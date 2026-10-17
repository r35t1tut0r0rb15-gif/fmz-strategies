"""RSI 14 divergences, long only, 30-minute bars: a confirmed RSI pivot low (1 bar left, 3 right) forming a regular or a
hidden bullish divergence with the previous pivot low (5 to 60 bars earlier) goes long; the RSI crossing above 80, or a
regular bearish divergence at a confirmed RSI pivot high, closes it.
Port of FMZ strategy #432315 "RSI离散分歧策略RSI-Divergence-Strategy" (RSI Divergence Indicator).

FMZ source id: 432315

Source
    https://www.fmz.com/strategy/432315 (PineScript v4, FMZ last modified 2023-11-16 11:36:45).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 179-374), RSI 14, pivots 1 / 3, range 5-60, take profit at RSI 80, stop type NONE
    bull = low[3] < valuewhen(pl, low[3], 1) and rsi[3] > valuewhen(pl, rsi[3], 1) and inRange(pl[1]) and pl
    hiddenBull = low[3] > valuewhen(pl, low[3], 1) and rsi[3] < valuewhen(pl, rsi[3], 1) and inRange(pl[1]) and pl
    bull or hiddenBull -> entry long;  crossover(rsi, 80) or bear (mirror on pivot highs) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * A pivot is found at bar t when bar t - 3 is strictly lower (higher) than the bar before it and
      the 3 bars after it (pivotlow / pivothigh, only past bars read). valuewhen(.., 1) is the value at
      the previous pivot; inRange counts the bars since the last pivot before this bar (barssince of
      pl[1]), 5 to 60.
    * The stop type is "NONE" (the trailing branches are input options and not ported). pyramiding 2
      lets a second signal add (criterion 4, not ported); a close on a bar that also signals is
      followed by that bar's re-entry, so the position stays open. Long only; Opposite entries
      cannot occur. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; pivots confirmed on past bars.
    2 generic: PASS, RSI divergences and levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity 2 and pyramiding 2 stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND366941 (4 members, best partner #439954, Jaccard 0.790); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432315_rsi_divergence_long"
FAMILY = "macd_divergence"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 9],
    "tp_level": [80, 70],
}
DEFAULT_PARAMS = {"rsi_len": 14, "lb_l": 1, "lb_r": 3, "tp_level": 80, "range_lo": 5, "range_hi": 60}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(x, n):
    d = x.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


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


def _since_prev(cond):
    """barssince(cond[1]): bars from the last bar before t where cond held, counted as Pine does."""
    m = len(cond)
    out = np.full(m, np.nan)
    last = -1
    for t in range(m):
        if t >= 1 and cond[t - 1]:
            last = t
        if last >= 0:
            out[t] = t - last
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    osc = _rsi(c, int(p["rsi_len"]))
    ov = osc.to_numpy(dtype=float)
    lb, rb = int(p["lb_l"]), int(p["lb_r"])
    pl = _pivots(ov, lb, rb, False)
    ph = _pivots(ov, lb, rb, True)
    o_r = osc.shift(rb).to_numpy(dtype=float)
    l_r = lo.shift(rb).to_numpy(dtype=float)
    h_r = h.shift(rb).to_numpy(dtype=float)
    r_lo, r_hi = float(p["range_lo"]), float(p["range_hi"])
    sp, sh = _since_prev(pl), _since_prev(ph)
    in_l = (sp >= r_lo) & (sp <= r_hi)
    in_h = (sh >= r_lo) & (sh <= r_hi)
    vo_l, vl_l = _vw1(pl, o_r), _vw1(pl, l_r)
    vo_h, vh_h = _vw1(ph, o_r), _vw1(ph, h_r)
    bull = pl & (l_r < vl_l) & (o_r > vo_l) & in_l
    hbull = pl & (l_r > vl_l) & (o_r < vo_l) & in_l
    bear = ph & (h_r > vh_h) & (o_r < vo_h) & in_h
    tp = float(p["tp_level"])
    xo = ((osc > tp) & (osc.shift(1) <= tp)).to_numpy()
    le_raw = bull | hbull
    lx_raw = xo | bear
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if le_raw[i]:
            pos = 1
        if lx_raw[i] and start == 1 and not le_raw[i]:
            pos = 0                                       # a same-bar signal re-opens the position
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, false, false.copy()))


def portfolio_kwargs(**params):
    return {}
