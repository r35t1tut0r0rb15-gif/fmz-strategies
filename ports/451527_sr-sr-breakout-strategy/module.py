"""Breakouts of a tested resistance / support zone, 10-minute bars: a green bar closing over the last 5 highs and over a cluster of at least 2 pivot highs (within a zone 3 % of the 300-bar range wide, from the last 71 bars) goes long; the mirror through pivot lows goes short; reversing.
Port of FMZ strategy #451527 "SR-突破策略-SR-Breakout-Strategy" (SR Breakout Strategy (LonesomeTheBlue / chanu_lev10k)).

FMZ source id: 451527

Source
    https://www.fmz.com/strategy/451527 (PineScript v5, FMZ last modified 2024-05-15 16:30:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-227), pivots 5 / 5; max breakout length 71; zone 3 % of the 300-bar range; minimum tests 2; SL / TP 18 % off by default
    pivot highs kept newest first, dropped from the old end beyond 71 bars;  close > open and close > highest(5)[1] -> walk the pivots under the close: bomax = their highest, count those within the zone under it
    count >= 2, open <= bomax and highest(5)[1] < bomax -> entry Long;  the mirror on pivot lows -> entry Short
    exit(stop = issl ? ... : na, limit = istp ? ... : na) with SL / TP off

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pivot arrays, the walk (stopped at the first pivot at or over the close) and the zone count
      are followed as written, bar by bar; a pivot is strict on both sides (as the house pivot
      helper) and is known prd bars after its bar. The zone width uses the high-low range of the last
      min(bar_index, 300) bars. The stop and target are off by default (issl / istp false), so the
      exits carry na levels and never act: positions end at the opposite entry. The two conditions
      cannot meet on one bar (green against red). REVERSAL INTENDED. No sizing code. FREQ = "10min"
      from the backtest header (UTC-aligned 10-minute bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, breakouts of multi-tested pivot zones.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451527_pivot_zone_breakout_reversal"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "prd": [5, 10],
    "bo_len": [71, 150],
    "width_pct": [3.0, 5.0],
}
DEFAULT_PARAMS = {"prd": 5, "bo_len": 71, "width_pct": 3.0, "mintest": 2}


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


def _zone(vals, close, open_, edge, width, mintest, up):
    """The breakout level as written, or nan: vals newest first; up = resistance (highs)."""
    if up:
        bo = vals[0]
        xx = 0
        for x in range(len(vals)):
            if vals[x] >= close:
                break
            xx = x
            bo = max(bo, vals[x])
        if not (xx >= mintest and open_ <= bo):
            return np.nan, 0
        num = sum(1 for x in range(xx + 1) if bo - width <= vals[x] <= bo)
        if num < mintest or edge >= bo:
            return np.nan, num
        return bo, num
    bo = vals[0]
    xx = 0
    for x in range(len(vals)):
        if vals[x] <= close:
            break
        xx = x
        bo = min(bo, vals[x])
    if not (xx >= mintest and open_ >= bo):
        return np.nan, 0
    num = sum(1 for x in range(xx + 1) if bo <= vals[x] <= bo + width)
    if num < mintest or edge <= bo:
        return np.nan, num
    return bo, num


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    prd, bo_len, mt = int(p["prd"]), int(p["bo_len"]), int(p["mintest"])
    rate = float(p["width_pct"]) / 100
    o = bars_df["open"].to_numpy(dtype=float)
    h = bars_df["high"].to_numpy(dtype=float)
    lo = bars_df["low"].to_numpy(dtype=float)
    c = bars_df["close"].to_numpy(dtype=float)
    m = len(c)
    ph, pl = _pivots(h, prd, prd, True), _pivots(lo, prd, prd, False)
    hgst = pd.Series(h).rolling(prd).max().shift(1).to_numpy()
    lwst = pd.Series(lo).rolling(prd).min().shift(1).to_numpy()
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    phv, phl, plv, pll = [], [], [], []
    for i in range(m):
        n = max(min(i, 300), 1)
        width = (h[i - n + 1:i + 1].max() - lo[i - n + 1:i + 1].min()) * rate
        if ph[i]:
            phv.insert(0, h[i - prd])
            phl.insert(0, i - prd)
            while len(phl) > 1 and i - phl[-1] > bo_len:
                phl.pop()
                phv.pop()
        if pl[i]:
            plv.insert(0, lo[i - prd])
            pll.insert(0, i - prd)
            while len(pll) > 1 and i - pll[-1] > bo_len:
                pll.pop()
                plv.pop()
        if len(phv) >= mt and c[i] > o[i] and c[i] > hgst[i]:
            bo, num = _zone(phv, c[i], o[i], hgst[i], width, mt, True)
            le[i] = not np.isnan(bo) and num >= mt
        if len(plv) >= mt and c[i] < o[i] and c[i] < lwst[i]:
            bo, num = _zone(plv, c[i], o[i], lwst[i], width, mt, False)
            se[i] = not np.isnan(bo) and num >= mt
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
