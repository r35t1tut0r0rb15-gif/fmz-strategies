"""Pivot support / resistance zones (pivots 10 / 10, up to 20 pivots clustered within 10 % of the 300-bar range, the 5 strongest zones with at least 2 pivots) with Bollinger 20 / 2, bar size from the driver, long only: the close crossing over a zone's mid-level while at or under the lower band buys; crossing under one while at or over the upper band closes.
Port of FMZ strategy #478687 "Dynamic Support Resistance Bollinger Bands Multi Indicator Cross Strategy" (Support Resistance & Bollinger & EMA21).

FMZ source id: 478687

Source
    https://www.fmz.com/strategy/478687 (PineScript v5, FMZ last modified 2025-01-17 14:24:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-259), pivot period 10, High/Low source; max 20 pivots; channel width 10 %; max 5 S/R; min strength 2; BB 20 / 2; EMA 21 plotted only
    on pivot bars: unshift the pivot value (20 kept); rebuild the zones: for each pivot, gather pivots within the channel width (strength = count), drop / replace overlapping weaker zones, keep the 5 strongest with strength >= 2
    crossed_over = any zone mid with close[1] <= mid < close;  crossed_over and close <= lower band -> entry Compra;  crossed_under and close >= upper band -> close Compra

Interpretation choices (Pine rules in SURVEY_README.md)
    * A loop rebuilds the zone lists on each pivot bar exactly as the script's arrays do (the zone levels
      persist between pivot bars; the strength list is rebuilt on each pivot bar). A pivot is confirmed 10
      bars after its centre bar (strict, as Pine's pivothigh / pivotlow); ta.highest(300) / ta.lowest(300)
      read the high and low, and no zone exists before 300 bars. The zone mid is not rounded to the
      instrument tick (round_to_mintick), which only moves it within one tick. The source has no
      backtest header and names no bar size: FREQ = "bar_size_pending"; precompute builds the bars with
      the house bar_sizes.build_bars with the driver's bar_size. Long only. No sizing code.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, pivot-zone crossings at the Bollinger extremes.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_478687_pivot_sr_zone_cross_bb20_extreme_long"
FAMILY = "support_resistance"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # no backtest header: the driver supplies bar_size
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "prd": [10, 5],
    "channel_w": [10, 5],
}
DEFAULT_PARAMS = {"prd": 10, "channel_w": 10, "max_pp": 20, "max_sr": 5, "min_strength": 2, "bb_length": 20}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def _pivot(x, side, span=5):
    """Strict pivot of x at t - span, confirmed at t (Pine ta.pivothigh / pivotlow on the chart bars)."""
    v = np.asarray(x, dtype=float)
    m = len(v)
    out = np.zeros(m, dtype=bool)
    for t in range(2 * span, m):
        c = v[t - span]
        rest = np.concatenate([v[t - 2 * span:t - span], v[t - span + 1:t + 1]])
        if np.isnan(c) or np.isnan(rest).any():
            continue
        out[t] = (c > rest).all() if side > 0 else (c < rest).all()
    return out


def _zone(piv, ind, cw):
    lo = hi = piv[ind]
    n = 0
    for cpp in piv:
        w = hi - cpp if cpp <= lo else cpp - lo
        if w <= cw:
            if cpp <= hi:
                lo = min(lo, cpp)
            else:
                hi = max(hi, cpp)
            n += 1
    return hi, lo, n


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k = int(p["prd"])
    ph, pl = _pivot(h, 1, k), _pivot(lo, -1, k)
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    cwid = ((h.rolling(300).max() - lo.rolling(300).min()) * float(p["channel_w"]) / 100).to_numpy()
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = 2 * c.rolling(n).std(ddof=0)
    at_low = (c <= basis - dev).to_numpy()
    at_high = (c >= basis + dev).to_numpy()
    max_pp, max_sr, min_st = int(p["max_pp"]), int(p["max_sr"]), int(p["min_strength"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    piv, up, dn = [], [], []
    for t in range(m):
        if ph[t] or pl[t]:
            piv.insert(0, hv[t - k] if ph[t] else lv[t - k])
            if len(piv) > max_pp:
                piv.pop()
            up, dn, st = [], [], []
            for x in range(len(piv)):
                zh, zl, zn = _zone(piv, x, cwid[t])
                ok = True
                for i in range(len(up)):
                    if (zl <= up[i] <= zh) or (zl <= dn[i] <= zh):
                        if zn >= st[i]:
                            del st[i], up[i], dn[i]
                        else:
                            ok = False
                        break
                if not ok:
                    continue
                loc = len(st)
                for i in range(len(st) - 1, -1, -1):
                    if zn <= st[i]:
                        break
                    loc = i
                if loc < max_sr and zn >= min_st:
                    st.insert(loc, zn)
                    up.insert(loc, zh)
                    dn.insert(loc, zl)
                    if len(st) > max_sr:
                        st.pop()
                        up.pop()
                        dn.pop()
        if t == 0:
            continue
        mids = [(a + b) / 2 for a, b in zip(up, dn)]
        over = any(cv[t - 1] <= md < cv[t] for md in mids)
        under = any(cv[t - 1] >= md > cv[t] for md in mids)
        le[t] = over and at_low[t]
        lx[t] = under and at_high[t]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
