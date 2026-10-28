"""Independent bar-by-bar ports of the published Pine source of popular
TradingView community scripts, compared with ``tv_indicators``.

Every port below was written from the published Pine code (see the URL in
each section), not from the library. The ``ta.*`` built-ins the scripts call
are re-implemented here in plain Python as TradingView defines them (SMA-seeded
EMA/RMA, population stdev, ``ta.atr = rma(tr(true))``, ...), so nothing from
``tv_indicators`` is used to build the expected values.

Pine semantics mirrored: ``x[1]`` is na on bar 0, comparisons with na are
false, ``nz()``, ``var`` vs re-initialised variables, ``math.max/min`` with na
return na, arithmetic with na gives na.

Tests that disagree with the published script are kept and marked
``xfail(strict=True)`` with the discrepancy in the reason.
"""

import inspect
import math

import numpy as np
import pytest

import tv_indicators as ti
from tv_indicators.tests.test_indicators import C, H, L, N, V, c, h, l, same, v

NA = float("nan")
TOL = dict(rtol=1e-7, atol=1e-7)


# ---------------------------------------------------------------------------
# Pine semantics helpers
# ---------------------------------------------------------------------------

def na(x):
    return x is None or (isinstance(x, float) and math.isnan(x))


def nz(x, r=0.0):
    return r if na(x) else x


def at(x, i, k=1):
    """``x[k]`` evaluated on bar ``i`` (na before the first bar)."""
    j = i - k
    return x[j] if j >= 0 else NA


def gt(a, b):
    return not na(a) and not na(b) and a > b


def lt(a, b):
    return not na(a) and not na(b) and a < b


def ge(a, b):
    return not na(a) and not na(b) and a >= b


def le(a, b):
    return not na(a) and not na(b) and a <= b


def eq(a, b):
    return not na(a) and not na(b) and a == b


def ne(a, b):
    return not na(a) and not na(b) and a != b


def pmax(a, b):
    return NA if na(a) or na(b) else max(a, b)


def pmin(a, b):
    return NA if na(a) or na(b) else min(a, b)


def pabs(a):
    return NA if na(a) else abs(a)


def add(a, b):
    return NA if na(a) or na(b) else a + b


def sub(a, b):
    return NA if na(a) or na(b) else a - b


def mul(a, b):
    return NA if na(a) or na(b) else a * b


def div(a, b):
    if na(a) or na(b) or b == 0:
        return NA
    return a / b


def L_(x):
    return [float(t) for t in np.asarray(x, float)]


# --- ta.* built-ins -------------------------------------------------------

def window(x, i, n):
    if i < n - 1:
        return None
    w = x[i - n + 1: i + 1]
    return None if any(na(t) for t in w) else w


def ta_sum(x, n):
    out = []
    for i in range(len(x)):
        w = window(x, i, n)
        out.append(NA if w is None else math.fsum(w))
    return out


def ta_sma(x, n):
    return [NA if na(s) else s / n for s in ta_sum(x, n)]


def ta_wma(x, n):
    norm = n * (n + 1) / 2
    out = []
    for i in range(len(x)):
        w = window(x, i, n)
        out.append(NA if w is None else math.fsum(w[j] * (j + 1) for j in range(n)) / norm)
    return out


def ta_stdev(x, n):
    out = []
    for i in range(len(x)):
        w = window(x, i, n)
        if w is None:
            out.append(NA)
            continue
        m = math.fsum(w) / n
        out.append(math.sqrt(math.fsum((t - m) ** 2 for t in w) / n))
    return out


def ta_dev(x, n):
    out = []
    for i in range(len(x)):
        w = window(x, i, n)
        if w is None:
            out.append(NA)
            continue
        m = math.fsum(w) / n
        out.append(math.fsum(abs(t - m) for t in w) / n)
    return out


def ta_highest(x, n):
    return [NA if (w := window(x, i, n)) is None else max(w) for i in range(len(x))]


def ta_lowest(x, n):
    return [NA if (w := window(x, i, n)) is None else min(w) for i in range(len(x))]


def ta_linreg(x, n, offset):
    """Least-squares line over the last n bars (oldest x=0) evaluated at n-1-offset."""
    out = []
    xs = list(range(n))
    mx = (n - 1) / 2
    sxx = math.fsum((t - mx) ** 2 for t in xs)
    for i in range(len(x)):
        w = window(x, i, n)
        if w is None:
            out.append(NA)
            continue
        my = math.fsum(w) / n
        slope = math.fsum((xs[j] - mx) * (w[j] - my) for j in range(n)) / sxx
        out.append(my + slope * (n - 1 - offset - mx))
    return out


def _ewm(x, n, alpha):
    """Pine ta.ema / ta.rma: na until n values, seeded with their SMA."""
    out = []
    state = NA
    run = 0
    for i, t in enumerate(x):
        if na(t):
            assert na(state), "na inside the series is not expected in these tests"
            out.append(NA)
            run = 0
            continue
        run += 1
        if na(state):
            if run >= n:
                state = math.fsum(x[i - n + 1: i + 1]) / n
        else:
            state = alpha * t + (1 - alpha) * state
        out.append(state)
    return out


def ta_ema(x, n):
    return _ewm(x, n, 2 / (n + 1))


def ta_rma(x, n):
    return _ewm(x, n, 1 / n)


def ta_change(x):
    return [sub(x[i], at(x, i)) for i in range(len(x))]


def ta_tr(hi, lo, cl, handle_na):
    out = []
    for i in range(len(hi)):
        if na(at(hi, i)):
            out.append(hi[i] - lo[i] if handle_na else NA)
        else:
            pc = cl[i - 1]
            out.append(max(hi[i] - lo[i], abs(hi[i] - pc), abs(lo[i] - pc)))
    return out


def ta_atr(hi, lo, cl, n):
    return ta_rma(ta_tr(hi, lo, cl, True), n)


def ta_rsi(x, n):
    ch = ta_change(x)
    u = ta_rma([pmax(t, 0.0) for t in ch], n)
    d = ta_rma([pmax(-t if not na(t) else NA, 0.0) for t in ch], n)
    out = []
    for a, b in zip(u, d):
        if na(a) or na(b):
            out.append(NA)
        elif b == 0:
            out.append(100.0)
        elif a == 0:
            out.append(0.0)
        else:
            out.append(100 - 100 / (1 + a / b))
    return out


def ta_cci(x, n):
    m, d = ta_sma(x, n), ta_dev(x, n)
    return [div(sub(x[i], m[i]), mul(0.015, d[i])) for i in range(len(x))]


def ta_mfi(src, vol, n):
    # pine_mfi from the reference manual: na comparisons are false, so bar 0
    # (change is na) lands in both sums.
    ch = ta_change(src)
    up = ta_sum([vol[i] * (0.0 if le(ch[i], 0.0) else src[i]) for i in range(len(src))], n)
    dn = ta_sum([vol[i] * (0.0 if ge(ch[i], 0.0) else src[i]) for i in range(len(src))], n)
    out = []
    for a, b in zip(up, dn):
        if na(a) or na(b):
            out.append(NA)
        elif b == 0:
            out.append(100.0)  # upper / 0 = inf -> 100
        else:
            out.append(100.0 - 100.0 / (1.0 + a / b))
    return out


def ta_crossover(a, b):
    return [gt(a[i], b[i]) and le(at(a, i), at(b, i)) for i in range(len(a))]


def ta_crossunder(a, b):
    return [lt(a[i], b[i]) and ge(at(a, i), at(b, i)) for i in range(len(a))]


def ta_cross(a, b):
    return [x or y for x, y in zip(ta_crossover(a, b), ta_crossunder(a, b))]


def ta_barssince(cond):
    out, last = [], None
    for i, t in enumerate(cond):
        if t:
            last = i
        out.append(NA if last is None else float(i - last))
    return out


def lag(x, k):
    return [at(x, i, k) for i in range(len(x))]


cl, hi, lo, vo = L_(c), L_(h), L_(l), L_(v)
hl2 = [(a + b) / 2 for a, b in zip(hi, lo)]
hlc3 = [(a + b + d) / 3 for a, b, d in zip(hi, lo, cl)]


def fl(x):
    return np.asarray(x, float)


def test_builtin_helpers_sanity():
    # The plain-Python built-ins agree with TA-Lib (independent of the library).
    talib = pytest.importorskip("talib")
    same(ta_ema(cl, 20), talib.EMA(c, 20), **TOL)
    same(ta_sma(cl, 20), talib.SMA(c, 20), **TOL)
    same(ta_wma(cl, 7), talib.WMA(c, 7), **TOL)
    same(ta_linreg(cl, 14, 0), talib.LINEARREG(c, 14), **TOL)
    same(ta_cci(hlc3, 20), talib.CCI(h, l, c, 20), **TOL)
    same(ta_highest(cl, 9), talib.MAX(c, 9), **TOL)


# ---------------------------------------------------------------------------
# 1. Range Filter Buy and Sell 5min [guikroth]
#    https://www.tradingview.com/script/J8GzFGfD/ (republish "true to the
#    guikroth version"); code: github.com/treebourks-debug/RangeFilter_MT5_EA
#    "Script_Range Filter Buy and Sell 5min.txt" (v5, @tvenn)
# 2. Twin Range Filter [colinmck] (v4), code: fmzquant/strategies
#    Twin-Range-Filter.md (header "(c) colinmck")
# ---------------------------------------------------------------------------

def pine_smoothrng(x, t, m):
    wper = t * 2 - 1
    avrng = ta_ema([pabs(sub(x[i], at(x, i))) for i in range(len(x))], t)
    return [mul(s, m) for s in ta_ema(avrng, wper)]


def pine_rngfilt_and_signals(src, smrng):
    n = len(src)
    filt, upward, downward, condini, long_c, short_c, hb, lb = ([] for _ in range(8))
    for i in range(n):
        x, r = src[i], smrng[i]
        p = nz(at(filt, i))
        if gt(x, p):
            f = p if lt(sub(x, r), p) else sub(x, r)
        else:
            f = p if gt(add(x, r), p) else add(x, r)
        filt.append(f)
        f1 = at(filt, i)
        up_prev, dn_prev = nz(at(upward, i)), nz(at(downward, i))
        upward.append(up_prev + 1 if gt(f, f1) else 0.0 if lt(f, f1) else up_prev)
        downward.append(dn_prev + 1 if lt(f, f1) else 0.0 if gt(f, f1) else dn_prev)
        hb.append(add(f, r))
        lb.append(sub(f, r))
        s1 = at(src, i)
        lc = (gt(x, f) and gt(x, s1) and upward[i] > 0) or (gt(x, f) and lt(x, s1) and upward[i] > 0)
        sc = (lt(x, f) and lt(x, s1) and downward[i] > 0) or (lt(x, f) and gt(x, s1) and downward[i] > 0)
        prev = at(condini, i)
        condini.append(1.0 if lc else -1.0 if sc else prev)
        long_c.append(lc and eq(prev, -1.0))
        short_c.append(sc and eq(prev, 1.0))
    return filt, hb, lb, upward, downward, condini, long_c, short_c


def test_range_filter_guikroth():
    exp = pine_rngfilt_and_signals(cl, pine_smoothrng(cl, 100, 3.0))
    got = ti.range_filter(C)
    for e, g in zip(exp, got):
        same(g, fl(e), **TOL)


def test_twin_range_filter_colinmck():
    s1, s2 = pine_smoothrng(cl, 27, 1.6), pine_smoothrng(cl, 55, 2.0)
    smrng = [div(add(a, b), 2) for a, b in zip(s1, s2)]
    filt, _, _, _, _, condini, lg, sh = pine_rngfilt_and_signals(cl, smrng)
    got = ti.twin_range_filter(C)
    for e, g in zip((filt, condini, lg, sh), got):
        same(g, fl(e), **TOL)


# ---------------------------------------------------------------------------
# 3. HalfTrend [everget]
#    https://www.tradingview.com/script/U1SJ8ubc-HalfTrend/
#    code: github.com/everget/tradingview-pinescript-indicators
#          trailing_stops/halftrend.pine (author's own repo, v6)
# ---------------------------------------------------------------------------

def pine_halftrend(amplitude=2, channel_deviation=2, partial_window=True):
    """``partial_window``: how ta.highestbars/lowestbars behave on the first
    amplitude-1 bars. With na there AND na-propagating math.min the script
    could never leave its initial state, so TradingView must do one of the
    two; partial windows (True) or skipping the na (False) give identical
    output (checked below)."""
    n = len(cl)
    atr2 = [div(a, 2) for a in ta_atr(hi, lo, cl, 100)]
    dev = [mul(channel_deviation, a) for a in atr2]
    if partial_window:
        high_price = [max(hi[max(0, i - amplitude + 1): i + 1]) for i in range(n)]
        low_price = [min(lo[max(0, i - amplitude + 1): i + 1]) for i in range(n)]
    else:
        high_price, low_price = ta_highest(hi, amplitude), ta_lowest(lo, amplitude)
    highma, lowma = ta_sma(hi, amplitude), ta_sma(lo, amplitude)
    mn, mx = (pmin, pmax) if partial_window else (
        lambda a, b: b if na(a) else pmin(a, b), lambda a, b: b if na(a) else pmax(a, b))

    trend = next_trend = 0
    max_low = nz(at(lo, 0), lo[0])
    min_high = nz(at(hi, 0), hi[0])
    up = down = 0.0
    up_hist, down_hist, trend_hist = [], [], []
    ht, tr_o, ah, al, buy, sell = [], [], [], [], [], []
    for i in range(n):
        arrow_up = arrow_down = NA
        if next_trend == 1:
            max_low = mx(low_price[i], max_low)
            if lt(highma[i], max_low) and lt(cl[i], nz(at(lo, i), lo[i])):
                trend, next_trend, min_high = 1, 0, high_price[i]
        else:
            min_high = mn(high_price[i], min_high)
            if gt(lowma[i], min_high) and gt(cl[i], nz(at(hi, i), hi[i])):
                trend, next_trend, max_low = 0, 1, low_price[i]
        t1 = at(trend_hist, i)
        if trend == 0:
            if not na(t1) and t1 != 0:
                d1 = at(down_hist, i)
                up = down if na(d1) else d1
                arrow_up = sub(up, atr2[i])
            else:
                u1 = at(up_hist, i)
                up = max_low if na(u1) else pmax(max_low, u1)
            atr_high, atr_low = add(up, dev[i]), sub(up, dev[i])
        else:
            if not na(t1) and t1 != 1:
                u1 = at(up_hist, i)
                down = up if na(u1) else u1
                arrow_down = add(down, atr2[i])
            else:
                d1 = at(down_hist, i)
                down = min_high if na(d1) else pmin(min_high, d1)
            atr_high, atr_low = add(down, dev[i]), sub(down, dev[i])
        up_hist.append(up)
        down_hist.append(down)
        trend_hist.append(trend)
        ht.append(up if trend == 0 else down)
        tr_o.append(float(trend))
        ah.append(atr_high)
        al.append(atr_low)
        buy.append(not na(arrow_up) and trend == 0 and eq(t1, 1))
        sell.append(not na(arrow_down) and trend == 1 and eq(t1, 0))
    return ht, tr_o, ah, al, buy, sell


def test_halftrend_everget():
    exp = pine_halftrend()
    alt = pine_halftrend(partial_window=False)
    got = ti.halftrend(H, L, C)
    for e, a, g in zip(exp, alt, got):
        same(a, fl(e), **TOL)
        same(g, fl(e), **TOL)


# ---------------------------------------------------------------------------
# 4. SSL channel [ErwinBeckers] (v3)
#    source quoted at community.tradovate.com/t/ssl-channel-chart-indicator/1173
#    (same lines in github.com/rajatjpatel/pine "ssl")
# ---------------------------------------------------------------------------

def test_ssl_channel_erwinbeckers():
    n = 10
    sma_h, sma_l = ta_sma(hi, n), ta_sma(lo, n)
    hlv, down, upl = [], [], []
    for i in range(len(cl)):
        hv = 1.0 if gt(cl[i], sma_h[i]) else -1.0 if lt(cl[i], sma_l[i]) else at(hlv, i)
        hlv.append(hv)
        down.append(sma_h[i] if lt(hv, 0) else sma_l[i])
        upl.append(sma_l[i] if lt(hv, 0) else sma_h[i])
    got = ti.ssl_channel(H, L, C)
    same(got.ssl_up, fl(upl), **TOL)
    same(got.ssl_down, fl(down), **TOL)
    same(got.hlv, fl(hlv), **TOL)


# ---------------------------------------------------------------------------
# 5. Trend Magic
#    KivancOzbilgic: https://www.tradingview.com/script/kRIjThLZ-Trend-Magic/
#      (page inputs: CCI period 20, ATR Multiplier 1, ATR Period 5, close);
#      code mirrored in github.com/crazyrabbitheart/SimpleStrategy-pinescript
#      Pinescript.txt and hasnocool/tradingview-pine-scripts "Strategy
#      Myth-Busting #11" ("Trend Magic by KivancOzbilgic")
#    glaz: https://www.tradingview.com/script/Wpy6qdyl-Trend-Magic/
#      (page inputs: CCI 20, ATR 5, ATR Multiplier 1, original coloring);
#      code mirrored ("Trend Magic code adapted from Glaz") in fmzquant/strategies
#      Multi-factor-Quantitative-Trading-Strategy.md and High-Low-Cryptocurrency...md
# ---------------------------------------------------------------------------

def pine_trend_magic_kivanc(period=20, coeff=1.0, ap=5):
    atr = ta_sma(ta_tr(hi, lo, cl, False), ap)
    cci = ta_cci(cl, period)
    mt = []
    for i in range(len(cl)):
        up_t = sub(lo[i], mul(atr[i], coeff))
        dn_t = add(hi[i], mul(atr[i], coeff))
        p = nz(at(mt, i))
        if ge(cci[i], 0):
            mt.append(p if lt(up_t, p) else up_t)
        else:
            mt.append(p if gt(dn_t, p) else dn_t)
    return mt, [ge(t, 0) for t in cci]


def pine_trend_magic_glaz(cci_n=20, atr_n=5, mult=1.0):
    this = ta_cci(cl, cci_n)
    atr = ta_sma(ta_tr(hi, lo, cl, False), atr_n)
    bu, bd, x = [], [], []
    for i in range(len(cl)):
        last = nz(at(this, i))
        dn = add(hi[i], mul(mult, atr[i]))
        upb = sub(lo[i], mul(mult, atr[i]))
        if ge(this[i], 0) and last < 0:
            upb = at(bd, i)
        if le(this[i], 0) and last > 0:
            dn = at(bu, i)
        if ge(this[i], 0):
            if lt(upb, at(bu, i)):
                upb = at(bu, i)
        else:
            if le(this[i], 0):
                if gt(dn, at(bd, i)):
                    dn = at(bd, i)
        bu.append(upb)
        bd.append(dn)
        x.append(upb if ge(this[i], 0) else dn if le(this[i], 0) else at(x, i))
    return x


def test_trend_magic_matches_kivanc():
    mt, bull = pine_trend_magic_kivanc()
    got = ti.trend_magic(H, L, C)
    same(got.magic_trend, fl(mt), **TOL)
    same(got.bullish, fl(bull), **TOL)


@pytest.mark.xfail(strict=True, reason=(
    "ti.trend_magic implements the KivancOzbilgic script, not glaz's: glaz seeds the "
    "new side from the other buffer on a CCI sign change (bufferUp := bufferDn[1]) "
    "and clamps against the same buffer's own history, so the lines differ"))
def test_trend_magic_matches_glaz():
    same(ti.trend_magic(H, L, C).magic_trend, fl(pine_trend_magic_glaz()), **TOL)


# ---------------------------------------------------------------------------
# 6. AlphaTrend [KivancOzbilgic] (v5)
#    https://www.tradingview.com/script/o50NYLAZ-AlphaTrend/ (page inputs:
#    Multiplier 1, Common Period 14, close, no-volume false); code:
#    fmzquant/strategies AlphaTrend.md and hasnocool/tradingview-pine-scripts
#    "AlphaTrend Strategy.pine" (header "(c) KivancOzbilgic")
# ---------------------------------------------------------------------------

def pine_alphatrend(coeff=1.0, ap=14, novolumedata=False):
    atr = ta_sma(ta_tr(hi, lo, cl, False), ap)
    osc = ta_rsi(cl, ap) if novolumedata else ta_mfi(hlc3, vo, ap)
    at_ = []
    for i in range(len(cl)):
        up_t = sub(lo[i], mul(atr[i], coeff))
        dn_t = add(hi[i], mul(atr[i], coeff))
        p = nz(at(at_, i))
        if ge(osc[i], 50):
            at_.append(p if lt(up_t, p) else up_t)
        else:
            at_.append(p if gt(dn_t, p) else dn_t)
    at2 = lag(at_, 2)
    buy_k, sell_k = ta_crossover(at_, at2), ta_crossunder(at_, at2)
    k1, k2 = ta_barssince(buy_k), ta_barssince(sell_k)
    o1 = ta_barssince([False] + buy_k[:-1])
    o2 = ta_barssince([False] + sell_k[:-1])
    buy = [b and gt(a, d) for b, a, d in zip(buy_k, o1, k2)]
    sell = [s and gt(a, d) for s, a, d in zip(sell_k, o2, k1)]
    return at_, at2, buy, sell, buy_k, sell_k


@pytest.mark.parametrize("novol", [False, True])
def test_alphatrend_kivanc(novol):
    exp = pine_alphatrend(novolumedata=novol)
    got = ti.alphatrend(H, L, C, V, use_rsi=novol)
    for e, g in zip(exp, got):
        same(g, fl(e), **TOL)


# ---------------------------------------------------------------------------
# 7. Optimized Trend Tracker [KivancOzbilgic] (v4, VAR average)
#    https://www.tradingview.com/script/zVhoDQME/ (inputs: OTT Period 2,
#    OTT Percent 1.4, MA type VAR); code: github.com/Indie-script/
#    indie-script.github.io indicators/Optimized Trend Tracker/*.pinescript4
# ---------------------------------------------------------------------------

def pine_var(src, length):
    valpha = 2 / (length + 1)
    vud1 = [sub(src[i], at(src, i)) if gt(src[i], at(src, i)) else 0.0 for i in range(len(src))]
    vdd1 = [sub(at(src, i), src[i]) if lt(src[i], at(src, i)) else 0.0 for i in range(len(src))]
    vud, vdd = ta_sum(vud1, 9), ta_sum(vdd1, 9)
    out = []
    for i in range(len(src)):
        cmo = nz(div(sub(vud[i], vdd[i]), add(vud[i], vdd[i])))
        out.append(nz(valpha * abs(cmo) * src[i]) + (1 - valpha * abs(cmo)) * nz(at(out, i)))
    return out


def pine_ott(length=2, percent=1.4):
    mavg = pine_var(cl, length)
    ls_h, ss_h, ott, dir_h = [], [], [], []
    d = 1
    for i in range(len(cl)):
        m = mavg[i]
        fark = m * percent * 0.01
        ls = m - fark
        lsp = nz(at(ls_h, i), ls)
        ls = pmax(ls, lsp) if gt(m, lsp) else ls
        ss = m + fark
        ssp = nz(at(ss_h, i), ss)
        ss = pmin(ss, ssp) if lt(m, ssp) else ss
        d = nz(at(dir_h, i), d)
        d = 1 if d == -1 and gt(m, ssp) else -1 if d == 1 and lt(m, lsp) else d
        mt = ls if d == 1 else ss
        ott.append(mt * (200 + percent) / 200 if gt(m, mt) else mt * (200 - percent) / 200)
        ls_h.append(ls)
        ss_h.append(ss)
        dir_h.append(d)
    ott2 = lag(ott, 2)
    return ott, ott2, mavg, [float(t) for t in dir_h], ta_crossover(mavg, ott2), ta_crossunder(mavg, ott2)


def test_vidya_is_kivanc_var():
    same(ti.vidya(C, 2), fl(pine_var(cl, 2)), **TOL)


def test_ott_kivanc():
    exp = pine_ott()
    got = ti.ott(C)
    for e, g in zip(exp, got):
        same(g, fl(e), **TOL)


# ---------------------------------------------------------------------------
# 8. SuperTrend [KivancOzbilgic] (v4)
#    https://www.tradingview.com/script/r6dAP7yi/ (inputs: ATR Period 10, hl2,
#    ATR Multiplier 3, Change ATR Calculation Method true); code:
#    Indie-script/indie-script.github.io indicators/SuperTrend/SuperTrend.pinescript4
# ---------------------------------------------------------------------------

def pine_supertrend_kivanc(periods=10, mult=3.0, change_atr=True):
    atr = ta_atr(hi, lo, cl, periods) if change_atr else ta_sma(ta_tr(hi, lo, cl, False), periods)
    up_h, dn_h, tr_h, st = [], [], [], []
    trend = 1
    for i in range(len(cl)):
        up = sub(hl2[i], mul(mult, atr[i]))
        up1 = nz(at(up_h, i), up)
        up = pmax(up, up1) if gt(at(cl, i), up1) else up
        dn = add(hl2[i], mul(mult, atr[i]))
        dn1 = nz(at(dn_h, i), dn)
        dn = pmin(dn, dn1) if lt(at(cl, i), dn1) else dn
        trend = nz(at(tr_h, i), trend)
        trend = 1 if trend == -1 and gt(cl[i], dn1) else -1 if trend == 1 and lt(cl[i], up1) else trend
        up_h.append(up)
        dn_h.append(dn)
        tr_h.append(trend)
        st.append(up if trend == 1 else dn)
    buy = [tr_h[i] == 1 and eq(at(tr_h, i), -1) for i in range(len(cl))]
    sell = [tr_h[i] == -1 and eq(at(tr_h, i), 1) for i in range(len(cl))]
    return st, [float(t) for t in tr_h], up_h, dn_h, buy, sell


@pytest.mark.parametrize("change_atr", [True, False])
def test_supertrend_kivanc(change_atr):
    exp = pine_supertrend_kivanc(change_atr=change_atr)
    got = ti.supertrend_kivanc(H, L, C, change_atr=change_atr)
    for e, g in zip(exp, got):
        same(g, fl(e), **TOL)


# ---------------------------------------------------------------------------
# 9. QQE. The original glaz "QQE" page/code was not found. The same core is in
#    "QQE signals" [colinmck] (v4), Indie-script/indie-script.github.io
#    indicators/QQE Signals/QQE Signals.pinescript4 (defaults 14 / 5 / 4.238),
#    and in "QQE MOD" [Mihkel00] ("By Glaz, Modified"),
#    https://www.tradingview.com/script/TpUW4muw/ (code: github.com/edyatl/qqe-mod
#    README; defaults RSI 6 / SF 5 / QQE 3, second QQE 6 / 5 / 1.61).
# ---------------------------------------------------------------------------

def pine_qqe(rsi_period=14, sf=5, qqe=4.238):
    wilders = rsi_period * 2 - 1
    rsi_ma = ta_ema(ta_rsi(cl, rsi_period), sf)
    atr_rsi = [pabs(sub(at(rsi_ma, i), rsi_ma[i])) for i in range(len(cl))]
    dar = [mul(t, qqe) for t in ta_ema(ta_ema(atr_rsi, wilders), wilders)]
    lb, sb, tr_h, tl = [], [], [], []
    for i in range(len(cl)):
        r, r1 = rsi_ma[i], at(rsi_ma, i)
        lb1, sb1 = at(lb, i), at(sb, i)
        nsb, nlb = add(r, dar[i]), sub(r, dar[i])
        lb.append(pmax(lb1, nlb) if gt(r1, lb1) and gt(r, lb1) else nlb)
        sb.append(pmin(sb1, nsb) if lt(r1, sb1) and lt(r, sb1) else nsb)
        # cross(RSIndex, shortband[1]) / cross(longband[1], RSIndex)
        x_a, x_b = r, sb1
        x_a1, x_b1 = r1, at(sb, i, 2)
        cross_sb = (gt(x_a, x_b) and le(x_a1, x_b1)) or (lt(x_a, x_b) and ge(x_a1, x_b1))
        y_a, y_b = lb1, r
        y_a1, y_b1 = at(lb, i, 2), r1
        cross_lb = (gt(y_a, y_b) and le(y_a1, y_b1)) or (lt(y_a, y_b) and ge(y_a1, y_b1))
        trend = 1.0 if cross_sb else -1.0 if cross_lb else nz(at(tr_h, i), 1.0)
        tr_h.append(trend)
        tl.append(lb[i] if trend == 1 else sb[i])
    return rsi_ma, tl, tr_h, lb, sb


@pytest.mark.parametrize("params", [(14, 5, 4.238), (6, 5, 3.0), (6, 5, 1.61)])
def test_qqe_core(params):
    exp = pine_qqe(*params)
    got = ti.qqe(C, *params)
    for e, g in zip(exp, got):
        same(g, fl(e), **TOL)


# ---------------------------------------------------------------------------
# 10. STC Indicator - A Better MACD [SHK]
#     https://www.tradingview.com/script/WhRRThMI-STC-Indicator-A-Better-MACD-SHK/
#     (page inputs: Length 12, FastLength 26, SlowLength 50, AAA 0.5); code:
#     github.com/koushiknagshuvo/STC-and-Halftrend-indicator "Stc indicator.txt"
#     (v5 copy, same 12/26/50/0.5). Strategy copies (UT Bot + STC) use 80/27/50.
# ---------------------------------------------------------------------------

def pine_stc(length=12, fast=26, slow=50, aaa=0.5):
    macd = [sub(a, b) for a, b in zip(ta_ema(cl, fast), ta_ema(cl, slow))]
    ccc, hh = ta_lowest(macd, length), ta_highest(macd, length)
    c5 = ddd = d6 = e5 = 0.0  # var ... = 0.0
    ddd_h, out = [], []
    for i in range(len(cl)):
        cccc = sub(hh[i], ccc[i])
        c5 = (macd[i] - ccc[i]) / cccc * 100 if gt(cccc, 0) else c5
        ddd = c5 if i == 0 else ddd + aaa * (c5 - ddd)  # na(DDD[1]) only on bar 0
        ddd_h.append(ddd)
        w = window(ddd_h, i, length)
        if w is not None:
            dddd = min(w)
            ddddd = max(w) - dddd
            d6 = (ddd - dddd) / ddddd * 100 if ddddd > 0 else d6
        e5 = d6 if i == 0 else e5 + aaa * (d6 - e5)
        out.append(e5)
    return out


def test_stc_shk():
    same(ti.schaff_trend_cycle(C), fl(pine_stc()), **TOL)
    same(ti.schaff_trend_cycle(C, 80, 27, 50), fl(pine_stc(80, 27, 50)), **TOL)


# ---------------------------------------------------------------------------
# 11. Waddah Attar Explosion [LazyBear]
#     https://www.tradingview.com/script/iu3kKWDI-Waddah-Attar-Explosion-LazyBear/
#     code: github.com/vuyelwadr/pulsechainTraderPdai
#           pine_scripts/146_waddah_attar_explosion.pine
#     Its dead zone is a constant input (deadZone = input(20)). The ATR dead zone
#     nz(rma(tr(true),100)) * 3.7 belongs to "Waddah Attar Explosion V2 [SHK]"
#     (https://www.tradingview.com/script/d9IjcYyS/, code in
#     github.com/rajatjpatel/pine "ssl").
# ---------------------------------------------------------------------------

def pine_wae(sensitivity=150, fast=20, slow=40, channel=20, mult=2.0):
    def calc_macd(src):
        return [sub(a, b) for a, b in zip(ta_ema(src, fast), ta_ema(src, slow))]
    m0 = calc_macd(cl)
    m1 = calc_macd([at(cl, i) for i in range(len(cl))])
    t1 = [mul(sub(a, b), sensitivity) for a, b in zip(m0, m1)]
    basis, sd = ta_sma(cl, channel), ta_stdev(cl, channel)
    e1 = [sub(add(b, mul(mult, s)), sub(b, mul(mult, s))) for b, s in zip(basis, sd)]
    up = [t if ge(t, 0) else 0.0 for t in t1]
    dn = [-t if lt(t, 0) else 0.0 for t in t1]
    return up, dn, e1


def test_waddah_attar_explosion_lazybear():
    up, dn, e1 = pine_wae()
    got = ti.waddah_attar_explosion(H, L, C)
    same(got.trend_up, fl(up), **TOL)
    same(got.trend_down, fl(dn), **TOL)
    same(got.explosion, fl(e1), **TOL)


def test_waddah_dead_zone_is_shk_v2_formula():
    dz = [nz(t) * 3.7 for t in ta_rma(ta_tr(hi, lo, cl, True), 100)]
    same(ti.waddah_attar_explosion(H, L, C).dead_zone, fl(dz), **TOL)


@pytest.mark.xfail(strict=True, reason=(
    "LazyBear's WAE plots deadZone = input(20) (a constant line); the library's "
    "dead_zone is nz(rma(tr(true),100))*3.7 from 'Waddah Attar Explosion V2 [SHK]'"))
def test_waddah_dead_zone_lazybear():
    same(ti.waddah_attar_explosion(H, L, C).dead_zone, np.full(N, 20.0), **TOL)


# ---------------------------------------------------------------------------
# 12. Volume Flow Indicator [LazyBear]
#     https://www.tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear/
#     code: pulsechainTraderPdai pine_scripts/102_volume_flow.pine and
#     Indie-script/indie-script.github.io indicators/Volume Flow Indicator
# ---------------------------------------------------------------------------

def pine_vfi(length=130, coef=0.2, vcoef=2.5, signal_length=5, smooth=False):
    typical = hlc3
    inter = [sub(math.log(typical[i]), math.log(at(typical, i))) if i > 0 else NA for i in range(N)]
    vinter = ta_stdev(inter, 30)
    cutoff = [mul(mul(coef, vinter[i]), cl[i]) for i in range(N)]
    vave = lag(ta_sma(vo, length), 1)
    vmax = [mul(t, vcoef) for t in vave]
    vc = [vo[i] if lt(vo[i], vmax[i]) else vmax[i] for i in range(N)]
    mf = ta_change(typical)
    vcp = []
    for i in range(N):
        neg = NA if na(cutoff[i]) else -cutoff[i]
        vcp.append(vc[i] if gt(mf[i], cutoff[i]) else (-vc[i] if not na(vc[i]) else NA)
                   if lt(mf[i], neg) else 0.0)
    raw = [div(s, a) for s, a in zip(ta_sum(vcp, length), vave)]
    vfi = ta_sma(raw, 3) if smooth else raw
    vfima = ta_ema(vfi, signal_length)
    return vfi, vfima, [sub(a, b) for a, b in zip(vfi, vfima)]


@pytest.mark.parametrize("smooth", [False, True])
def test_vfi_lazybear(smooth):
    exp = pine_vfi(smooth=smooth)
    got = ti.vfi(H, L, C, V, smooth=smooth)
    for e, g in zip(exp, got):
        same(g, fl(e), **TOL)


# ---------------------------------------------------------------------------
# 13. Coral Trend Indicator [LazyBear]
#     https://www.tradingview.com/script/qyUwc2Al-Coral-Trend-Indicator-LazyBear/
#     code: pulsechainTraderPdai pine_scripts/160_coral_trend.pine
# ---------------------------------------------------------------------------

def pine_coral(sm=21, cd=0.4):
    di = (sm - 1.0) / 2.0 + 1.0
    c1 = 2 / (di + 1.0)
    c2 = 1 - c1
    c3 = 3.0 * (cd * cd + cd * cd * cd)
    c4 = -3.0 * (2.0 * cd * cd + cd + cd * cd * cd)
    c5 = 3.0 * cd + 1.0 + cd * cd * cd + 3.0 * cd * cd
    i1, i2, i3, i4, i5, i6, out = ([] for _ in range(7))
    for i in range(N):
        i1.append(c1 * cl[i] + c2 * nz(at(i1, i)))
        i2.append(c1 * i1[i] + c2 * nz(at(i2, i)))
        i3.append(c1 * i2[i] + c2 * nz(at(i3, i)))
        i4.append(c1 * i3[i] + c2 * nz(at(i4, i)))
        i5.append(c1 * i4[i] + c2 * nz(at(i5, i)))
        i6.append(c1 * i5[i] + c2 * nz(at(i6, i)))
        out.append(-cd * cd * cd * i6[i] + c3 * i5[i] + c4 * i4[i] + c5 * i3[i])
    return out


def test_coral_lazybear():
    same(ti.coral(C), fl(pine_coral()), **TOL)


# ---------------------------------------------------------------------------
# 14. CM_Williams_Vix_Fix [ChrisMoody]
#     https://www.tradingview.com/script/og7JPrRA/ ; code:
#     github.com/czarcrab/tv-indicators-strategies CM_Williams_Vix_Fix.tv
# ---------------------------------------------------------------------------

def test_williams_vix_fix_chrismoody(pd_=22, bbl=20, mult=2.0, lb=50, ph=0.85):
    hc = ta_highest(cl, pd_)
    wvf = [mul(div(sub(hc[i], lo[i]), hc[i]), 100) for i in range(N)]
    sdev = [mul(mult, t) for t in ta_stdev(wvf, bbl)]
    upper = [add(m, s) for m, s in zip(ta_sma(wvf, bbl), sdev)]
    rh = [mul(t, ph) for t in ta_highest(wvf, lb)]
    sig = [ge(w, u) or ge(w, r) for w, u, r in zip(wvf, upper, rh)]
    got = ti.williams_vix_fix(L, C)
    for e, g in zip((wvf, upper, rh, sig), got):
        same(g, fl(e), **TOL)


# ---------------------------------------------------------------------------
# 15a. Laguerre RSI. LazyBear's script was NOT found (www.tradingview.com/
#      script/PFsgmnZW/ is gone and no mirror was found). Compared instead with
#      KivancOzbilgic's "Laguerre RSI" (v3), github.com/rajatjpatel/pine
#      "Laguerre RSI.txt" (= jubayernil/all-pine-script), which has
#      gamma = 1 - alpha and plots 100 * LaRSI.
# 15b. Ehlers Instantaneous Trend [LazyBear]
#      https://www.tradingview.com/script/DaHLcICg/ ; code:
#      pulsechainTraderPdai pine_scripts/194_ehlers_instant_trend.pine
# ---------------------------------------------------------------------------

def pine_laguerre_rsi_kivanc(alpha):
    g = 1 - alpha
    l0, l1, l2, l3, out = [], [], [], [], []
    for i in range(N):
        l0.append((1 - g) * cl[i] + g * nz(at(l0, i)))
        l1.append(-g * l0[i] + nz(at(l0, i)) + g * nz(at(l1, i)))
        l2.append(-g * l1[i] + nz(at(l1, i)) + g * nz(at(l2, i)))
        l3.append(-g * l2[i] + nz(at(l2, i)) + g * nz(at(l3, i)))
        a, b, cc, d = l0[i], l1[i], l2[i], l3[i]
        cu = (a - b if a > b else 0) + (b - cc if b > cc else 0) + (cc - d if cc > d else 0)
        cd = (b - a if a < b else 0) + (cc - b if b < cc else 0) + (d - cc if cc < d else 0)
        temp = -1 if cu + cd == 0 else cu + cd
        out.append(0.0 if temp == -1 else cu / temp)
    return out


@pytest.mark.parametrize("gamma", [0.5, 0.8])
def test_laguerre_rsi_formula(gamma):
    same(ti.laguerre_rsi(C, gamma), fl(pine_laguerre_rsi_kivanc(1 - gamma)), **TOL)


def test_itrend_lazybear(a=0.07):
    src = hl2
    it = []
    for i in range(N):
        s0, s1, s2 = src[i], at(src, i), at(src, i, 2)
        fb = NA if na(s1) or na(s2) else (s0 + 2 * s1 + s2) / 4.0
        if na(fb):
            it.append(NA)
            continue
        it.append((a - a * a / 4.0) * s0 + 0.5 * a * a * s1 - (a - 0.75 * a * a) * s2
                  + 2 * (1 - a) * nz(at(it, i), fb) - (1 - a) * (1 - a) * nz(at(it, i, 2), fb))
    trig = [sub(2.0 * t if not na(t) else NA, nz(at(it, i, 2))) for i, t in enumerate(it)]
    got = ti.itrend(H, L)
    same(got.itrend, fl(it), **TOL)
    same(got.trigger, fl(trig), **TOL)


# ---------------------------------------------------------------------------
# 16. MavilimW [KivancOzbilgic] (v4), code: Indie-script/indie-script.github.io
#     indicators/MavilimW (Fibonacci WMA Cascade)/*.pinescript4
#     ZLSMA - Zero Lag LSMA [veryfid], https://www.tradingview.com/script/3LGnSrQN/
#     (page inputs: Length 32, Offset 0, close); code block "(c) veryfid" in
#     fmzquant/strategies Trend-Following-Strategy-Based-on-Moving-Average-and-MACD.md
# ---------------------------------------------------------------------------

def test_mavilimw_kivanc(fmal=3, smal=5):
    tmal = fmal + smal
    Fmal = smal + tmal
    Ftmal = tmal + Fmal
    Smal = Fmal + Ftmal
    m = cl
    for n in (fmal, smal, tmal, Fmal, Ftmal, Smal):
        m = ta_wma(m, n)
    same(ti.mavilimw(C), fl(m), **TOL)


@pytest.mark.parametrize("length,offset", [(32, 0), (50, 2)])
def test_zlsma_veryfid(length, offset):
    lsma = ta_linreg(cl, length, offset)
    lsma2 = ta_linreg(lsma, length, offset)
    zl = [add(a, sub(a, b)) for a, b in zip(lsma, lsma2)]
    same(ti.zlsma(C, length, offset), fl(zl), **TOL)


# ---------------------------------------------------------------------------
# 17. Nadaraya-Watson Envelope [LuxAlgo], repaint = false (endpoint method)
#     https://www.tradingview.com/script/Iko0E2kL/ (inputs: Bandwidth 8, mult 3,
#     close, Repainting Smoothing true); code: github.com/marz-hunter/xauusd
#     "scalping-5min/Nadaraya-Watson Envelope [LuxAlgo]" (v5, (c) LuxAlgo)
# ---------------------------------------------------------------------------

def test_nadaraya_watson_luxalgo_endpoint(hband=8.0, mult=3.0):
    coefs = [math.exp(-(i ** 2) / (hband * hband * 2)) for i in range(500)]
    den = math.fsum(coefs)
    out = []
    for b in range(N):
        s = 0.0
        for i in range(500):
            s = add(s, mul(at(cl, b, i), coefs[i]))  # src[i] is na before bar 0
        out.append(div(s, den))
    mae = [mul(t, mult) for t in ta_sma([pabs(sub(cl[i], out[i])) for i in range(N)], 499)]
    got = ti.nadaraya_watson(C)
    same(got.estimate, fl(out), **TOL)
    same(got.upper, fl([add(a, b) for a, b in zip(out, mae)]), **TOL)
    same(got.lower, fl([sub(a, b) for a, b in zip(out, mae)]), **TOL)


# ---------------------------------------------------------------------------
# 18. SMI [UCSgears], https://www.tradingview.com/script/xd8t6hai/ ; code:
#     github.com/deskiziarecords/TRADE pine-scripts/STOC-UCS ("Code by UCSgears",
#     a = 5 Percent K Length, b = 3 Percent D Length; same defaults in
#     amico1234/fintech555 and deepentropy/lightweight-charts-indicators)
# ---------------------------------------------------------------------------

def pine_smi_ucs(a=5, b=3):
    ll, hh = ta_lowest(lo, a), ta_highest(hi, a)
    diff = [sub(x, y) for x, y in zip(hh, ll)]
    rdiff = [sub(cl[i], div(add(hh[i], ll[i]), 2)) for i in range(N)]
    avgrel = ta_ema(ta_ema(rdiff, b), b)
    avgdiff = ta_ema(ta_ema(diff, b), b)
    smi = [div(r, d / 2) * 100 if ne(d, 0) else 0.0 for r, d in zip(avgrel, avgdiff)]
    return smi, ta_ema(smi, b)


def test_smi_ucsgears_after_warmup():
    smi, sig = pine_smi_ucs()
    got = ti.smi(H, L, C, k_length=5, d_length=3)
    same(got[0], fl(smi), tail=N - 100, **TOL)
    same(got[1], fl(sig), tail=N - 100, **TOL)


@pytest.mark.xfail(strict=True, reason=(
    "UCSgears: SMI = avgdiff != 0 ? ... : 0, and na != 0 is false, so the script "
    "plots 0 (not na) while the double EMA warms up; its signal ema(SMI, 3) then "
    "starts at bar 2. The library returns na there (warm-up only, converges later)"))
def test_smi_ucsgears_warmup():
    smi, sig = pine_smi_ucs()
    got = ti.smi(H, L, C, k_length=5, d_length=3)
    same(got[0], fl(smi), **TOL)
    same(got[1], fl(sig), **TOL)


# ---------------------------------------------------------------------------
# Default inputs vs the published scripts
# ---------------------------------------------------------------------------

PUBLISHED_DEFAULTS = [
    (ti.range_filter, dict(period=100, multiplier=3.0)),
    (ti.twin_range_filter, dict(fast_period=27, fast_range=1.6, slow_period=55, slow_range=2.0)),
    (ti.halftrend, dict(amplitude=2, channel_deviation=2)),
    (ti.ssl_channel, dict(length=10)),
    (ti.trend_magic, dict(cci_period=20, atr_multiplier=1, atr_period=5)),
    (ti.alphatrend, dict(coeff=1, period=14, use_rsi=False)),
    (ti.ott, dict(length=2, percent=1.4)),
    (ti.supertrend_kivanc, dict(period=10, multiplier=3.0, change_atr=True)),
    (ti.qqe, dict(rsi_length=14, smoothing=5, factor=4.238)),
    (ti.schaff_trend_cycle, dict(length=12, fast=26, slow=50, factor=0.5)),
    (ti.waddah_attar_explosion, dict(sensitivity=150, fast=20, slow=40, channel_length=20, mult=2.0)),
    (ti.vfi, dict(length=130, coef=0.2, vcoef=2.5, signal_length=5, smooth=False)),
    (ti.coral, dict(smoothing=21, constant_d=0.4)),
    (ti.williams_vix_fix, dict(period=22, bb_length=20, mult=2.0, lookback=50, percentile=0.85)),
    (ti.itrend, dict(alpha=0.07)),
    (ti.mavilimw, dict(first_length=3, second_length=5)),
    (ti.zlsma, dict(length=32, offset=0)),
    (ti.nadaraya_watson, dict(bandwidth=8.0, mult=3.0)),
    pytest.param(ti.smi, dict(k_length=5, d_length=3), marks=pytest.mark.xfail(
        strict=True, reason="UCSgears SMI defaults are Percent K Length 5 / Percent D Length 3; "
                            "library k_length=10 (and ema_length=10 is an extra line not in the script)")),
]


@pytest.mark.parametrize("fn,expected", PUBLISHED_DEFAULTS)
def test_published_default_inputs(fn, expected):
    sig = inspect.signature(getattr(fn, "__wrapped__", fn))
    for name, val in expected.items():
        assert sig.parameters[name].default == val, (fn.__name__, name)
