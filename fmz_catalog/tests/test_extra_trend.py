"""Tests for fmz_catalog/extra_trend.py.

Each indicator is compared with a literal bar-by-bar Python port of its
reference Pine code (the published TradingView script, or the FMZ strategy's
own function for strategy-specific ones). Built-ins such as ta.atr / ta.ema /
ta.rsi come from tv_indicators, which is verified elsewhere. Pine semantics
are mirrored by the helpers below: na comparisons are false, math.max/min
with na give na, nz() seeds, x[n] is na before bar n.
"""

import math

import numpy as np
import pandas as pd
import pytest

import fmz_catalog.extra as fx
import fmz_catalog.extra_trend as xt
import tv_indicators as ti
from tv_indicators import kernels as kk
from tv_indicators.tests.test_indicators import TAIL, C, D, H, L, N, O, V, c, h, l, o, same, v

nan = float("nan")


# ---------------------------------------------------------------------------
# Pine helpers
# ---------------------------------------------------------------------------

def na(x):
    return x is None or (isinstance(x, float) and math.isnan(x))


def nz(x, r=0.0):
    return r if na(x) else x


def pmax(*a):
    return nan if any(na(x) for x in a) else max(a)


def pmin(*a):
    return nan if any(na(x) for x in a) else min(a)


def ne(a, b):
    return not na(a) and not na(b) and a != b


def at(x, i):
    """x[i] with Pine's na before the first bar."""
    return x[i] if 0 <= i < len(x) else nan


def roll(x, n, f):
    x = np.asarray(x, float)
    out = np.full(len(x), nan)
    for i in range(n - 1, len(x)):
        w = x[i - n + 1:i + 1]
        if not np.isnan(w).any():
            out[i] = f(w)
    return out


def p_sma(x, n):
    return roll(x, n, np.mean)


def p_sum(x, n):
    return roll(x, n, np.sum)


def p_stdev(x, n):
    return roll(x, n, lambda w: math.sqrt(np.mean((w - w.mean()) ** 2)))


def p_wma(x, n):
    wts = np.arange(1, n + 1)
    return roll(x, n, lambda w: (w * wts).sum() / wts.sum())


def p_highest(x, n):
    return roll(x, n, np.max)


def p_lowest(x, n):
    return roll(x, n, np.min)


def p_tr(handle_na):
    out = []
    for i in range(N):
        if i == 0:
            out.append(h[0] - l[0] if handle_na else nan)
        else:
            out.append(max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])))
    return np.array(out)


def p_barssince(cond):
    out, last = [], None
    for i, x in enumerate(cond):
        if x:
            last = i
        out.append(nan if last is None else i - last)
    return np.array(out, float)


def lt(a, b):
    return np.array([x < y for x, y in zip(a, b)])


def p_cross_over(a, b):
    return np.array([i > 0 and a[i] > b[i] and a[i - 1] <= b[i - 1] for i in range(len(a))])


def p_cross_under(a, b):
    return np.array([i > 0 and a[i] < b[i] and a[i - 1] >= b[i - 1] for i in range(len(a))])


def boolsame(a, b):
    np.testing.assert_array_equal(np.asarray(a, bool), np.asarray(b, bool))


ATR = {n: ti.atr(H, L, C, n).to_numpy() for n in (5, 7, 8, 10, 14, 26, 34, 52, 120, 200)}


# ---------------------------------------------------------------------------
# G-Channel
# ---------------------------------------------------------------------------

def test_g_channel_matches_jaggedsoft_g_trend():
    n = 100
    A, B = [], []
    for i in range(N):
        a1, b1 = at(A, i - 1), at(B, i - 1)
        A.append(pmax(c[i], nz(a1)) - nz(a1 - b1) / n)
        B.append(pmin(c[i], nz(b1)) + nz(a1 - b1) / n)
    crossup = [i > 0 and B[i - 1] < c[i - 1] and B[i] > c[i] for i in range(N)]
    crossdn = [i > 0 and A[i - 1] < c[i - 1] and A[i] > c[i] for i in range(N)]
    bullish = p_barssince(crossdn) <= p_barssince(crossup)
    r = xt.g_channel(C, n)
    same(r.upper, A)
    same(r.lower, B)
    same(r.avg, (np.array(A) + np.array(B)) / 2)
    boolsame(r.bullish, bullish)


def test_g_channel_source_seed_matches_na_seeded_copies():
    n = 100
    A, B = [], []
    for i in range(N):  # 双均线价格通道 copy (id 2f92c395f980 / fe44fbdbd4c1)
        a1, b1 = at(A, i - 1), at(B, i - 1)
        A.append(c[i] if na(a1) else max(c[i], a1) - (a1 - b1) / n)
        B.append(c[i] if na(b1) else min(c[i], b1) + (a1 - b1) / n)
    r = xt.g_channel(C, n, seed="source")
    same(r.upper, A)
    same(r.lower, B)
    same(r.upper, xt.g_channel(C, n).upper, tail=1000, rtol=1e-6)  # converges to the original


# ---------------------------------------------------------------------------
# TD Sequential / DeMark
# ---------------------------------------------------------------------------

def test_td_counts_match_strategy_copies():
    TS, TD, heat = [], [], []
    for i in range(N):
        c4 = at(c, i - 4)
        TS.append(nz(at(TS, i - 1)) + 1 if c[i] < c4 else 0)
        TD.append(nz(at(TD, i - 1)) + 1 if c[i] > c4 else 0)
        p = at(heat, i - 1)
        heat.append((1 if p == 13 else nz(p) + 1) if c[i] < c4 else 0)  # heat-map buySetup
    r = xt.td_sequential(H, L, C)
    same(r.buy_count, TS)
    same(r.sell_count, TD)
    bc = r.buy_count.to_numpy()
    same(np.where(bc > 0, (bc - 1) % 13 + 1, 0), heat)


def _td_rules_port(lb=4):
    """Perl's TD Setup / Countdown rules, bar by bar."""
    out = {k_: [] for k_ in ("bs", "ss", "bd", "sd", "bp", "sp", "bc", "sc", "b13", "s13", "res", "sup")}
    sb = ss = 0
    res = sup = nan
    buy = None  # dict(count, q, hi, tr)
    sell = None
    for i in range(N):
        c4 = at(c, i - lb)
        flip_dn = at(c, i - 1) > at(c, i - 1 - lb)
        flip_up = at(c, i - 1) < at(c, i - 1 - lb)
        sb = (sb + 1 if sb > 0 else (1 if flip_dn else 0)) if c[i] < c4 else 0
        ss = (ss + 1 if ss > 0 else (1 if flip_up else 0)) if c[i] > c4 else 0
        bd, sd, bp, sp, b13, s13 = sb == 9, ss == 9, False, False, False, False

        def setup_range():
            th = [max(h[j], c[j - 1]) if j >= 1 else h[j] for j in range(i - 8, i + 1)]
            tl = [min(l[j], c[j - 1]) if j >= 1 else l[j] for j in range(i - 8, i + 1)]
            return max(th), min(tl)

        if bd:
            bp = min(l[i], l[i - 1]) <= min(l[i - 2], l[i - 3])
            hi, lo = setup_range()
            res = hi
            sell = None
            if buy is None or buy["tr"] <= hi - lo < 1.618 * buy["tr"]:
                buy = dict(count=0, q=nan, hi=hi, tr=hi - lo)
        if sd:
            sp = max(h[i], h[i - 1]) >= max(h[i - 2], h[i - 3])
            hi, lo = setup_range()
            sup = lo
            buy = None
            if sell is None or sell["tr"] <= hi - lo < 1.618 * sell["tr"]:
                sell = dict(count=0, q=nan, lo=lo, tr=hi - lo)
        if buy is not None and i >= 1 and min(l[i], c[i - 1]) > buy["hi"]:
            buy = None
        if sell is not None and i >= 1 and max(h[i], c[i - 1]) < sell["lo"]:
            sell = None
        if buy is not None and i >= 2 and c[i] <= l[i - 2]:
            if buy["count"] < 12:
                buy["count"] += 1
                if buy["count"] == 8:
                    buy["q"] = c[i]
            elif l[i] <= buy["q"]:
                buy["count"] = 13
                b13 = True
        if sell is not None and i >= 2 and c[i] >= h[i - 2]:
            if sell["count"] < 12:
                sell["count"] += 1
                if sell["count"] == 8:
                    sell["q"] = c[i]
            elif h[i] >= sell["q"]:
                sell["count"] = 13
                s13 = True
        for key, val in (("bs", sb), ("ss", ss), ("bd", bd), ("sd", sd), ("bp", bp), ("sp", sp),
                         ("bc", buy["count"] if buy else 0), ("sc", sell["count"] if sell else 0),
                         ("b13", b13), ("s13", s13), ("res", res), ("sup", sup)):
            out[key].append(val)
        if b13:
            buy = None
        if s13:
            sell = None
    return out


def test_td_sequential_rules_port():
    p = _td_rules_port()
    r = xt.td_sequential(H, L, C)
    same(r.buy_setup, p["bs"])
    same(r.sell_setup, p["ss"])
    boolsame(r.buy_setup_complete, p["bd"])
    boolsame(r.sell_setup_complete, p["sd"])
    boolsame(r.buy_perfected, p["bp"])
    boolsame(r.sell_perfected, p["sp"])
    same(r.buy_countdown, p["bc"])
    same(r.sell_countdown, p["sc"])
    boolsame(r.buy_13, p["b13"])
    boolsame(r.sell_13, p["s13"])
    same(r.tdst_resistance, p["res"])
    same(r.tdst_support, p["sup"])
    # the data exercises every branch
    assert r.buy_setup_complete.sum() > 5 and r.sell_setup_complete.sum() > 5
    assert r.buy_13.sum() > 0 and r.sell_13.sum() > 0
    assert (r.buy_setup.to_numpy() <= r.buy_count.to_numpy()).all()


@pytest.mark.parametrize("length,lb", [(9, 4), (4, 4)])
def test_demark_reversal_points_cheatcountry(length, lb):
    drp, sig, U, Dn = [], [], [], []
    for i in range(N):
        u = d = 0
        for j in range(length):
            a, b = nz(at(c, i - j)), nz(at(c, i - j - lb))
            u += a > b
            d += a < b
        x = 1 if d == length else -1 if u == length else 0
        drp.append(x)
        sig.append(1 if x > 0 or u > d else -1 if x < 0 or d > u else 0)
        U.append(u)
        Dn.append(d)
    r = xt.demark_reversal_points(C, length, lb)
    same(r.drp, drp)
    same(r.signal, sig)
    same(r.up_count, U)
    same(r.down_count, Dn)


# ---------------------------------------------------------------------------
# Renko and Sizeblock
# ---------------------------------------------------------------------------

def _renko_port(size_fn):
    bricks = []  # (open, close)
    ref = None
    BO, BC, DR, NB = [], [], [], []
    for i in range(N):
        x = c[i]
        nb = 0
        if ref is None:
            ref = x
        else:
            while True:
                last_c = bricks[-1][1] if bricks else ref
                d = 0 if not bricks else (1 if bricks[-1][1] > bricks[-1][0] else -1)
                s = size_fn(i, last_c)
                if na(s) or s <= 0:
                    break
                if d >= 0 and x >= last_c + s:
                    bricks.append((last_c, last_c + s))
                    nb += 1
                elif d <= 0 and x <= last_c - s:
                    bricks.append((last_c, last_c - s))
                    nb -= 1
                elif d == 1 and x <= bricks[-1][0] - s:
                    bricks.append((bricks[-1][0], bricks[-1][0] - s))
                    nb -= 1
                elif d == -1 and x >= bricks[-1][0] + s:
                    bricks.append((bricks[-1][0], bricks[-1][0] + s))
                    nb += 1
                else:
                    break
        if bricks:
            BO.append(bricks[-1][0])
            BC.append(bricks[-1][1])
            DR.append(1 if bricks[-1][1] > bricks[-1][0] else -1)
        else:
            BO.append(nan)
            BC.append(nan)
            DR.append(0)
        NB.append(nb)
    return BO, BC, DR, NB


@pytest.mark.parametrize("method", ["atr", "traditional", "percentage"])
def test_renko_tradingview_rules(method):
    atr = ATR[14]
    fn = {"atr": lambda i, lc: atr[i], "traditional": lambda i, lc: 0.8,
          "percentage": lambda i, lc: lc * 0.5 / 100}[method]
    BO, BC, DR, NB = _renko_port(fn)
    r = xt.renko(H, L, C, method=method, box_size=0.8, percent=0.5)
    same(r.brick_open, BO)
    same(r.brick_close, BC)
    same(r.direction, DR)
    same(r.new_bricks, NB)
    assert np.abs(r.new_bricks).max() >= 1
    # reversals need two boxes: no brick ever closes inside the previous brick
    assert (np.abs(np.diff(r.brick_close.dropna().unique())) > 0).all()


@pytest.mark.parametrize("mintick,src", [(0.0, "close"), (0.01, "close"), (0.01, "highlow")])
def test_sizeblock_port(mintick, src):
    def rtm(x):
        return math.floor(x / mintick + 0.5) * mintick if mintick > 0 else x

    dv, ub = 1.0, 2.0
    X, Hh, Ll = [], [], []
    for i in range(N):
        a, b = o[i], c[i]
        cc = rtm(h[i]) if src == "highlow" else rtm(b)
        dd = rtm(l[i]) if src == "highlow" else rtm(b)
        x = rtm(a)
        x = nz(at(X, i - 1), x)
        hh = rtm(x * (1 + dv / 100))
        ll = rtm(x * (1 - dv / 100))
        hh = nz(at(Hh, i - 1), hh)
        ll = nz(at(Ll, i - 1), ll)
        if cc >= hh and b > a:
            while cc >= hh:
                x = hh
                hh = rtm(hh * (1 + dv / 100))
                ll = rtm(x * (1 - ub / 100))
        if dd <= ll and b < a:
            while dd <= ll:
                x = ll
                ll = rtm(ll * (1 - dv / 100))
                hh = rtm(x * (1 + ub / 100))
        X.append(x)
        Hh.append(hh)
        Ll.append(ll)
    r = xt.sizeblock(O, H, L, C, dv, ub, source=src, mintick=mintick)
    same(r.mid, X)
    same(r.upper, Hh)
    same(r.lower, Ll)


# ---------------------------------------------------------------------------
# Pivot Point SuperTrend
# ---------------------------------------------------------------------------

def _pine_pivot(x, left, right, high=True):
    out = [nan] * N
    for i in range(left + right, N):
        p = x[i - right]
        if high:
            ok = all(p > x[i - right - j] for j in range(1, left + 1)) and \
                all(p >= x[i - right + j] for j in range(1, right + 1))
        else:
            ok = all(p < x[i - right - j] for j in range(1, left + 1)) and \
                all(p <= x[i - right + j] for j in range(1, right + 1))
        if ok:
            out[i] = p
    return out


def test_private_pivot_matches_extra_tv():
    xtv = pytest.importorskip("fmz_catalog.extra_tv")
    for left, right in ((2, 2), (5, 3)):
        same(xt._pivot_nb(h.reshape(-1, 1), left, right, 1.0)[:, 0], xtv.pivothigh(H, left, right).pivot)
        same(xt._pivot_nb(l.reshape(-1, 1), left, right, -1.0)[:, 0], xtv.pivotlow(L, left, right).pivot)


def test_pivot_point_supertrend_lonesometheblue():
    prd, factor, pd_ = 2, 3.0, 10
    ph, pl = _pine_pivot(h, prd, prd), _pine_pivot(l, prd, prd, False)
    atr = ATR[pd_]
    center = nan
    CEN, TU, TD_, TR, ST, SUP, RES = [], [], [], [], [], [], []
    sup = res = nan
    for i in range(N):
        lastpp = ph[i] if not na(ph[i]) else (pl[i] if not na(pl[i]) else nan)
        if not na(lastpp) and lastpp:
            center = lastpp if na(center) else (center * 2 + lastpp) / 3
        up = center - factor * atr[i]
        dn = center + factor * atr[i]
        tu1, td1 = at(TU, i - 1), at(TD_, i - 1)
        tu = pmax(up, tu1) if at(c, i - 1) > tu1 else up
        td = pmin(dn, td1) if at(c, i - 1) < td1 else dn
        tr = 1 if c[i] > td1 else -1 if c[i] < tu1 else nz(at(TR, i - 1), 1)
        sup = pl[i] if not na(pl[i]) else sup
        res = ph[i] if not na(ph[i]) else res
        CEN.append(center)
        TU.append(tu)
        TD_.append(td)
        TR.append(tr)
        ST.append(tu if tr == 1 else td)
        SUP.append(sup)
        RES.append(res)
    r = xt.pivot_point_supertrend(H, L, C, prd, factor, pd_)
    same(r.supertrend, ST)
    same(r.trend, TR)
    same(r.center, CEN)
    same(r.up, TU)
    same(r.down, TD_)
    same(r.support, SUP)
    same(r.resistance, RES)
    boolsame(r.buy, [i > 0 and TR[i] == 1 and TR[i - 1] == -1 for i in range(N)])
    boolsame(r.sell, [i > 0 and TR[i] == -1 and TR[i - 1] == 1 for i in range(N)])


# ---------------------------------------------------------------------------
# Range Filter [DW]
# ---------------------------------------------------------------------------

class CondEMA:
    def __init__(self, n):
        self.val, self.ema, self.n = [], nan, n

    def __call__(self, x, cond):
        if cond:
            self.val.append(x)
            if len(self.val) > 1:
                self.val.pop(0)
            if na(self.ema):
                self.ema = self.val[0]
            self.ema = (self.val[0] - self.ema) * (2 / (self.n + 1)) + self.ema
        return self.ema


class CondSMA:
    def __init__(self, n):
        self.vals, self.n = [], n

    def __call__(self, x, cond):
        if cond:
            self.vals.append(x)
            if len(self.vals) > self.n:
                self.vals.pop(0)
        return sum(self.vals) / len(self.vals) if self.vals else nan


def _rf_dw_port(ftype, mov, scale, qty, n, smooth, sn, av, avn):
    hv = h if mov == "Wicks" else c
    lv = l if mov == "Wicks" else c
    e_atr, e_ac, s2, s1, e_r = CondEMA(n), CondEMA(n), CondSMA(n), CondSMA(n), CondEMA(sn)
    e_f, e_h, e_l = CondEMA(avn), CondEMA(avn), CondEMA(avn)
    tr = p_tr(True)
    rfilt = None
    F, HB, LB, F1 = [], [], [], []
    for i in range(N):
        hh, ll = hv[i], lv[i]
        x = (hh + ll) / 2
        x1 = (at(hv, i - 1) + at(lv, i - 1)) / 2
        atr_ = e_atr(tr[i], True)
        ac = e_ac(abs(x - x1), True)
        var = s2(x * x, True) - s1(x, True) ** 2
        sd = math.sqrt(var) if var >= 0 else nan
        rng = {"Average Change": qty * ac, "ATR": qty * atr_, "Standard Deviation": qty * sd,
               "% of Price": c[i] * qty / 100, "Absolute": qty}[scale]
        rs = e_r(rng, True)
        r = rs if smooth else rng
        if rfilt is None:
            rfilt = [(hh + ll) / 2] * 2
        rfilt[1] = rfilt[0]
        if ftype == 1:
            if hh - r > rfilt[1]:
                rfilt[0] = hh - r
            if ll + r < rfilt[1]:
                rfilt[0] = ll + r
        else:
            if hh >= rfilt[1] + r:
                rfilt[0] = rfilt[1] + math.floor(abs(hh - rfilt[1]) / r) * r
            if ll <= rfilt[1] - r:
                rfilt[0] = rfilt[1] - math.floor(abs(ll - rfilt[1]) / r) * r
        f1 = rfilt[0]
        cond = ne(f1, at(F1, i - 1))
        F1.append(f1)
        f2, h2, l2 = e_f(f1, cond), e_h(f1 + r, cond), e_l(f1 - r, cond)
        F.append(f2 if av else f1)
        HB.append(h2 if av else f1 + r)
        LB.append(l2 if av else f1 - r)
    fd, d = [], 0
    for i in range(N):
        d = 1 if at(F, i - 1) < F[i] else -1 if at(F, i - 1) > F[i] else d
        fd.append(d)
    return F, HB, LB, fd


@pytest.mark.parametrize("ftype,mov,scale,smooth,av", [
    (1, "Close", "Average Change", True, False),   # script defaults
    (1, "Close", "Average Change", True, True),    # FMZ copies' setting
    (2, "Wicks", "ATR", True, True),
    (1, "Wicks", "Standard Deviation", False, False),
    (2, "Close", "% of Price", False, True),
])
def test_range_filter_dw_port(ftype, mov, scale, smooth, av):
    qty = 2.618 if scale != "% of Price" else 1.5
    F, HB, LB, fd = _rf_dw_port(ftype, mov, scale, qty, 14, smooth, 27, av, 2)
    r = xt.range_filter_dw(H, L, C, ftype, mov, qty, scale, 14, smooth, 27, av, 2)
    same(r.filter, F)
    same(r.high_band, HB)
    same(r.low_band, LB)
    same(r.direction, fd)


# ---------------------------------------------------------------------------
# Leledc
# ---------------------------------------------------------------------------

def _lele_port(qual, ln, close_val=4, k_back=1):
    hh, ll = p_highest(h, ln), p_lowest(l, ln)
    bh, sh, out = [], [], []
    for i in range(N):
        b = nz(at(bh, i - k_back), 0)
        s = nz(at(sh, i - k_back), 0)
        ret = 0
        if c[i] > at(c, i - close_val):
            b += 1
        if c[i] < at(c, i - close_val):
            s += 1
        if b > qual and c[i] < o[i] and h[i] >= hh[i]:
            b, ret = 0, -1
        if s > qual and c[i] > o[i] and l[i] <= ll[i]:
            s, ret = 0, 1
        bh.append(b)
        sh.append(s)
        out.append(ret)
    return out


@pytest.mark.parametrize("k_back", [1, 2])
def test_leledc_joy_bangla(k_back):
    r = xt.leledc_exhaustion(O, H, L, C, index_lookback=k_back)
    same(r.major, _lele_port(6, 30, 4, k_back))
    same(r.minor, _lele_port(5, 5, 4, k_back))
    assert (r.major != 0).sum() > 5


# ---------------------------------------------------------------------------
# QuantNomad significant pivots
# ---------------------------------------------------------------------------

def test_pivot_atr_quantnomad():
    left, right, n, mult = 4, 2, 14, 0.1
    atr = ATR[n]
    PH, PL = [], []
    for i in range(N):
        a = atr[i] * mult
        ok_h = ok_l = True
        for j in range(1, left + 1):
            if at(h, i - right) < at(h, i - right - j) + a:
                ok_h = False
            if at(l, i - right) > at(l, i - right - j) - a:
                ok_l = False
        for j in range(right):
            if at(h, i - right) < h[i - j] + a:
                ok_h = False
            if at(l, i - right) > l[i - j] - a:
                ok_l = False
        PH.append(at(h, i - right) if ok_h else nan)
        PL.append(at(l, i - right) if ok_l else nan)
    r = xt.pivot_atr(H, L, C, left, right, n, mult)
    start = max(left + right, n - 1)
    same(r.pivot_high[start:], PH[start:])
    same(r.pivot_low[start:], PL[start:])
    # the script's warm-up flags every bar (na comparisons are false); ours does not
    assert np.isfinite(PH[right:start]).all() and r.pivot_high[:start].isna().all()


# ---------------------------------------------------------------------------
# OLS regression
# ---------------------------------------------------------------------------

def test_ols_regression_is_real_ols():
    n = 21
    A, B = [], []
    for i in range(N):
        if i < n - 1:
            A.append(nan)
            B.append(nan)
            continue
        b, a = np.polyfit(v[i - n + 1:i + 1], c[i - n + 1:i + 1], 1)
        A.append(a)
        B.append(b)
    r = xt.ols_regression(C, V, n)
    same(r.slope, B, rtol=1e-6, atol=1e-12)
    same(r.intercept, A, rtol=1e-6)
    # the FMZ linregs() copy subtracts each bar's own rolling mean: not OLS
    ybar, xbar = p_sma(c, n), p_sma(v, n)
    bad = p_sum((v - xbar) * (c - ybar), n) / p_sum((v - xbar) ** 2, n)
    m = ~np.isnan(bad)
    assert not np.allclose(bad[m], np.array(B)[m], rtol=1e-3)


# ---------------------------------------------------------------------------
# MOST and PMax
# ---------------------------------------------------------------------------

def _kivanc_stop_port(mavg, dist):
    LS, SS, DIR, OUT = [], [], [], []
    for i in range(N):
        m = mavg[i]
        ls = m - dist[i]
        lsp = nz(at(LS, i - 1), ls)
        ls = pmax(ls, lsp) if m > lsp else ls
        ss = m + dist[i]
        ssp = nz(at(SS, i - 1), ss)
        ss = pmin(ss, ssp) if m < ssp else ss
        d = nz(at(DIR, i - 1), 1)
        d = 1 if d == -1 and m > ssp else -1 if d == 1 and m < lsp else d
        LS.append(ls)
        SS.append(ss)
        DIR.append(d)
        OUT.append(ls if d == 1 else ss)
    return OUT, DIR


def test_most_kivanc_port_and_ott_line():
    from tv_indicators.community import _ott_nb
    ema = ti.ema(C, 3).to_numpy()
    most_, d = _kivanc_stop_port(ema, ema * 2.0 * 0.01)
    r = xt.most(C, 3, 2.0)
    same(r.most, most_)
    same(r.direction, d)
    same(r.most, _ott_nb(ema.reshape(-1, 1), 2.0)[1][:, 0])


def test_most_trailing_matches_moving_average_tracking_stop_loss():
    ma = ti.ema(C, 28).to_numpy()  # the copy offers many MAs; EMA here
    stop = ma * 0.038
    M = []
    for i in range(N):
        p = nz(at(M, i - 1), 0)
        a, a1 = ma[i], at(ma, i - 1)
        if a > p and a1 > p:
            x = pmax(p, a - stop[i])
        elif a < p and a1 < p:
            x = pmin(p, a + stop[i])
        else:
            x = a - stop[i] if a > p else a + stop[i]
        M.append(x)
    r = xt.most(C, 28, 3.8, "ema", method="trailing")
    same(r.most, M)


def _kivanc_ma_port(src, n, mav):
    if mav == "SMA":
        return p_sma(src, n)
    if mav == "EMA":
        return ti.ema(pd.Series(src), n).to_numpy()
    if mav == "WMA":
        return p_wma(src, n)
    if mav == "TMA":
        return p_sma(p_sma(src, math.ceil(n / 2)), n // 2 + 1)
    if mav == "VAR":
        a = 2 / (n + 1)
        vud = [src[i] - src[i - 1] if i and src[i] > src[i - 1] else 0 for i in range(N)]
        vdd = [src[i - 1] - src[i] if i and src[i] < src[i - 1] else 0 for i in range(N)]
        ud, dd = p_sum(vud, 9), p_sum(vdd, 9)
        out = []
        for i in range(N):
            cmo = nz((ud[i] - dd[i]) / (ud[i] + dd[i]) if (ud[i] + dd[i]) != 0 else nan)
            out.append(nz(a * abs(cmo) * src[i]) + (1 - a * abs(cmo)) * nz(at(out, i - 1)))
        return np.array(out)
    if mav == "WWMA":
        out = []
        for i in range(N):
            out.append(1 / n * src[i] + (1 - 1 / n) * nz(at(out, i - 1)))
        return np.array(out)
    if mav == "ZLEMA":
        lag = n // 2 if n / 2 == round(n / 2) else (n - 1) // 2
        return ti.ema(pd.Series(src + (src - pd.Series(src).shift(lag).to_numpy())), n).to_numpy()
    if mav == "TSF":
        s2 = src.reshape(-1, 1)
        lrc = kk.linreg_nb(s2, n, 0)[:, 0]
        return lrc + (lrc - kk.linreg_nb(s2, n, 1)[:, 0])
    raise AssertionError(mav)


@pytest.mark.parametrize("mav", ["EMA", "SMA", "WMA", "TMA", "VAR", "WWMA", "ZLEMA", "TSF"])
def test_pmax_kivanc_port(mav):
    src = (h + l) / 2
    mavg = _kivanc_ma_port(src, 10, mav)
    pm, d = _kivanc_stop_port(mavg, 3.0 * ATR[10])
    r = xt.pmax(H, L, C, 10, 3.0, mav, 10)
    same(r.mavg, mavg, rtol=1e-8)
    same(r.pmax, pm, rtol=1e-8)
    same(r.direction, d)
    boolsame(r.buy, p_cross_over(mavg, pm))
    boolsame(r.sell, p_cross_under(mavg, pm))


def test_pmax_sma_tr_and_normalize_and_core():
    src = (h + l) / 2
    mavg = _kivanc_ma_port(src, 10, "EMA")
    atr2 = p_sma(p_tr(False), 10)
    pm, d = _kivanc_stop_port(mavg, 3.0 * atr2)
    same(xt.pmax(H, L, C, change_atr=False).pmax, pm)
    pm, d = _kivanc_stop_port(mavg, 3.0 * ATR[10] / c)
    same(xt.pmax(H, L, C, normalize=True).pmax, pm)
    rsi = ti.rsi(C, 14).to_numpy()
    t3 = ti.t3(pd.Series(rsi), 8).to_numpy()
    fake_atr = p_sma(np.abs(np.diff(rsi, prepend=nan)), 10)
    pm, d = _kivanc_stop_port(t3, 3.0 * fake_atr)
    rc = xt.pmax_core(pd.Series(t3), pd.Series(fake_atr), 3.0)
    same(rc.pmax, pm)
    same(rc.direction, d)


# ---------------------------------------------------------------------------
# ATR stops and bands written inside strategies
# ---------------------------------------------------------------------------

def test_atr_trailing_support_port():
    atr = ATR[14]
    T = []
    for i in range(N):
        al = l[i] - atr[i]
        t = al
        t = t if na(at(T, i - 1)) else (al if al >= T[i - 1] else T[i - 1])
        t = al if c[i] <= t else t
        T.append(t)
    same(xt.atr_trailing_support(H, L, C, 14), T)


@pytest.mark.parametrize("wick", ["avg", "max"])
def test_atr_trailing_bands_river(wick):
    n_atr, mult, n = 5, 4, 30
    uwick = [nan if i == 0 else (h[i - 1] - o[i - 1] if c[i - 1] <= o[i - 1] else h[i - 1] - c[i - 1])
             for i in range(N)]
    lwick = [nan if i == 0 else (o[i - 1] - l[i - 1] if c[i - 1] > o[i - 1] else c[i - 1] - l[i - 1])
             for i in range(N)]
    f = p_sma if wick == "avg" else p_highest
    uw, lw = f(uwick, n), f(lwick, n)
    nloss = mult * ATR[n_atr]
    U, Lo, T, P = [], [], [], []
    for i in range(N):
        pu, pl_, pt = nz(at(U, i - 1), 0), nz(at(Lo, i - 1), 0), nz(at(T, i - 1), 0)
        hu, ll_ = h[i] + nloss[i] + uw[i], l[i] - nloss[i] - lw[i]
        u = pmin(nz(at(U, i - 1)), hu) if h[i] < pu and at(h, i - 1) < pu else hu
        lo = pmax(nz(at(Lo, i - 1)), ll_) if l[i] > pl_ and at(l, i - 1) > pl_ else ll_
        if l[i] > pt and at(l, i - 1) > pt:
            t = pmax(pt, ll_)
        elif h[i] < pt and at(h, i - 1) < pt:
            t = pmin(pt, hu)
        elif l[i] <= pt and at(c, i - 1) > pt:
            t = at(U, i - 1)
        elif h[i] >= pt and at(c, i - 1) < pt:
            t = at(Lo, i - 1)
        else:
            t = 0
        p = 1 if at(c, i - 1) > pt and l[i] <= pt else -1 if at(c, i - 1) < pt and h[i] >= pt else nz(at(P, i - 1), 0)
        U.append(u)
        Lo.append(lo)
        T.append(t)
        P.append(p)
    r = xt.atr_trailing_bands(O, H, L, C, n_atr, mult, n, wick)
    same(r.upper, U)
    same(r.lower, Lo)
    same(r.stop, T)
    same(r.pos, P)


def test_atr_breakout_bands_claw_pattern():
    atr = ATR[120]
    U, Lo = [], []
    for i in range(N):
        lt_, ut = l[i] - 2 * atr[i], h[i] + 2 * atr[i]
        ut = at(U, i - 1) if ut > at(U, i - 1) and c[i] < at(U, i - 1) else ut
        lt_ = at(Lo, i - 1) if lt_ < at(Lo, i - 1) and c[i] > at(Lo, i - 1) else lt_
        U.append(ut)
        Lo.append(lt_)
    u1 = [at(U, i - 1) for i in range(N)]
    l1 = [at(Lo, i - 1) for i in range(N)]
    cu = p_cross_over(c, u1) | p_cross_under(c, u1)
    cl = p_cross_over(c, l1) | p_cross_under(c, l1)
    st = np.where(p_barssince(cu) > p_barssince(cl), -1, 1)
    r = xt.atr_breakout_bands(H, L, C, 120, 2)
    same(r.upper, U)
    same(r.lower, Lo)
    same(r.state, st)


def test_wilder_volatility_trail_sparkyflary():
    n, mult = 7, 3.0
    atr = ti.rma(pd.Series(p_tr(False)), n).to_numpy()
    upper = p_lowest(c, n) + mult * atr
    lower = p_highest(c, n) - mult * atr
    TS = []
    for i in range(N):  # the script, `float TS = 0` included
        t1 = at(TS, i - 1)
        TS.append(at(upper, i - 1) if c[i] < t1 else at(lower, i - 1) if c[i] > t1 else 0.0)
    r = xt.wilder_volatility_trail(H, L, C, mult, n)
    same(r.upper_trail, upper)
    same(r.lower_trail, lower)
    TS = np.array(TS)
    ok = np.isfinite(TS) & (TS != 0)
    ok[:2 * n] = False
    same(r.stop[ok], TS[ok])
    assert ok.sum() > N - 50


def test_trend_trader_abraham():
    n, mult = 21, 3.0
    avg = p_wma(p_tr(False), n)
    hi = [at(p_highest(h, n), i - 1) - at(avg, i - 1) * mult for i in range(N)]
    lo = [at(p_lowest(l, n), i - 1) + at(avg, i - 1) * mult for i in range(N)]
    R, P = [], []
    for i in range(N):
        x = c[i]
        r_ = hi[i] if x > hi[i] and x > lo[i] else lo[i] if x < lo[i] and x < hi[i] else nz(at(R, i - 1), 0)
        p = 1 if x > r_ else -1 if x < r_ else nz(at(P, i - 1), 0)
        R.append(r_)
        P.append(p)
    r = xt.trend_trader(H, L, C, n, mult)
    same(r.trend_line, R)
    same(r.pos, P)


def test_trailing_stop_flip_river():
    lo_off, so_off = 1.5, 1.7
    T = []
    for i in range(N):
        t1, t2 = at(T, i - 1), at(T, i - 2)
        if l[i] <= t1 and at(l, i - 1) >= t2:
            t = c[i] + so_off
        elif h[i] >= t1 and at(h, i - 1) <= t2:
            t = c[i] - lo_off
        elif h[i] > t1:
            t = max(h[i] - lo_off, t1)
        elif l[i] < t1:
            t = min(l[i] + so_off, t1)
        else:
            t = c[i]
        T.append(t)
    same(xt.trailing_stop_flip(H, L, C, lo_off, so_off), T)


# ---------------------------------------------------------------------------
# Volumatic VIDYA, TrendScore, Recursive Bands
# ---------------------------------------------------------------------------

def test_volumatic_vidya_bigbeluga():
    vl, vm, dist = 10, 20, 2.0
    mom = [nan] + list(np.diff(c))
    pos = p_sum([m if m >= 0 else 0.0 for m in mom], vm)
    neg = p_sum([0.0 if m >= 0 else -m for m in mom], vm)
    alpha = 2 / (vl + 1)
    VV = []
    for i in range(N):
        cmo = abs(100 * (pos[i] - neg[i]) / (pos[i] + neg[i])) if (pos[i] + neg[i]) != 0 else nan
        VV.append(alpha * cmo / 100 * c[i] + (1 - alpha * cmo / 100) * nz(at(VV, i - 1)))
    vid = p_sma(VV, 15)
    up, lo = vid + ATR[200] * dist, vid - ATR[200] * dist
    xu, xd = p_cross_over(c, up), p_cross_under(c, lo)
    trend, trail, t = [], [], False
    for i in range(N):
        prev = t
        if xu[i]:
            t = True
        if xd[i]:
            t = False
        trend.append(t)
        trail.append(nan if (i > 0 and t != prev) else (lo[i] if t else up[i]))
    r = xt.volumatic_vidya(H, L, C, vl, vm, dist)
    same(r.vidya, vid)
    same(r.upper, up)
    same(r.lower, lo)
    boolsame(r.trend_up, trend)
    same(r.trail, trail)


def test_trend_score_chande():
    a, b = 10, 14  # the FMZ copy's inputs
    S = []
    for i in range(N):
        s = 0
        for j in range(a, b + 1):
            s += 1 if c[i] >= nz(at(c, i - j)) else -1
        S.append(s)
    r = xt.trend_score(C, a, b)
    same(r[b:], S[b:])
    assert r[:b].isna().all()
    assert xt.trend_score(C).abs().max() == 10


@pytest.mark.parametrize("method", ["classic", "atr", "stdev", "ahlr", "rfv"])
def test_recursive_bands_alexgrover(method):
    n = 100
    sc = 2 / (n + 1)
    rfv = []
    for i in range(N):
        rising = i >= n and all(c[i] > c[i - j] for j in range(1, n + 1))
        falling = i >= n and all(c[i] < c[i - j] for j in range(1, n + 1))
        rfv.append(abs(c[i] - c[i - 1]) if rising or falling else at(rfv, i - 1))
    vol = {"atr": ti.atr(H, L, C, n).to_numpy(), "stdev": p_stdev(c, n), "ahlr": p_sma(h - l, n),
           "rfv": np.array(rfv, float)}

    def vf(x, i):
        return x if method == "classic" else vol[method][i]

    A, B = [], []
    for i in range(N):
        s = c[i]
        a1, b1 = nz(at(A, i - 1), s), nz(at(B, i - 1), s)
        A.append(pmax(a1, s) - sc * vf(abs(s - a1), i))
        B.append(pmin(b1, s) + sc * vf(abs(s - b1), i))
    r = xt.recursive_bands(H, L, C, n, method)
    same(r.upper, A)
    same(r.lower, B)
    same(r.middle, (np.array(A) + np.array(B)) / 2)


# ---------------------------------------------------------------------------
# Other strategy-specific formulas
# ---------------------------------------------------------------------------

def test_adaptive_ls_trend_occ_port():
    n, sc = 24, 0.2
    S, B, LS, OSC = [], [], [], []
    cum = 0.0
    alpha = nan
    for i in range(N):
        s = sc * c[i] + (1 - sc) * nz(at(LS, i - 1), c[i])
        S.append(s)
        if i >= n:
            den = sum(abs(S[i - j] - S[i - j - 1]) for j in range(n))
            er = 1 - abs(s - S[i - n]) / den if den else nan
        else:
            er = nan
        pb = nz(at(B, i - 1), s)
        cum += abs(s - pb)
        a = cum / i * (1 + er) if i else nan
        b = s if s > pb + a else s if s < pb - a else pb
        B.append(b)
        ls = nan
        if i >= n - 1:
            ws, wb = np.array(S[i - n + 1:]), np.array(B[i - n + 1:])
            dev_s, dev_b = ws - ws.mean(), wb - wb.mean()
            dev_s[np.abs(dev_s) <= 1e-10] = 0  # Pine's ta.stdev epsilon
            dev_b[np.abs(dev_b) <= 1e-10] = 0
            if (dev_s ** 2).sum() > 0 and (dev_b ** 2).sum() > 0:
                alpha = np.corrcoef(ws, wb)[0, 1] * (ws.std() / wb.std())
            ls = alpha * b + (ws.mean() - alpha * wb.mean())
        LS.append(ls)
        b1 = at(B, i - 1)
        OSC.append(1 if b > b1 else 0 if b < b1 else at(OSC, i - 1))
    r = xt.adaptive_ls_trend(C, n, sc)
    same(r.trail, B, rtol=1e-7)
    same(r.ls, LS, rtol=1e-6)
    same(r.osc, OSC)


def test_logistic_price_forecast_port():
    net = [v[i] if i and 100 * (c[i] - c[i - 1]) / c[i - 1] > 0 else -v[i] for i in range(N)]
    z = p_sma(net, 10) / p_stdev(net, 100)
    sd = p_stdev(c, 20)
    pred = (c + sd) / (1 + sd / c * np.exp(-z))
    r = xt.logistic_price_forecast(C, V)
    same(r.forecast, pred)
    same(r.z, z)


def test_atr_envelope_multigrain():
    src = fx.jma(C, 144, 34).to_numpy()
    atr = ATR[34] * 3
    W = []
    for i in range(N):
        W.append(atr[i] if ne(src[i] - at(src, i - 1), 0) else at(W, i - 1))
    r = xt.atr_envelope(pd.Series(src, index=C.index), H, L, C, 34, 3)
    same(r.upper, src + np.array(W))
    same(r.lower, src - np.array(W))


def test_avellaneda_stoikov_quotes():
    g, s, T, k_ = 2.0, 8.0, 0.0833, 5.0
    mid = (c + np.r_[nan, c[:-1]]) / 2
    r = xt.avellaneda_stoikov_quotes(C, g, s, T, k_)
    same(r.bid, mid - k_ * g * s * s * T)
    same(r.ask, mid + k_ * g * s * s * T)
    r2 = xt.avellaneda_stoikov_quotes(C, 0.1, 0.02, 1.0, 1.5, model="as2008", inventory=2)
    rr = c - 2 * 0.1 * 0.02 ** 2
    half = (0.1 * 0.02 ** 2 + 2 / 0.1 * math.log(1 + 0.1 / 1.5)) / 2
    same(r2.bid, rr - half)
    same(r2.ask, rr + half)


def test_dual_thrust_capissimo_algos():
    def hl(n):
        return ([at(p_highest(h, n), i - 1) for i in range(N)], [at(p_highest(c, n), i - 1) for i in range(N)],
                [at(p_lowest(c, n), i - 1) for i in range(N)], [at(p_lowest(l, n), i - 1) for i in range(N)])

    k1, k2 = 0.7, 0.4
    hh, hc, lc, ll = hl(5)
    rng = [pmax(a - b, x - y) for a, b, x, y in zip(hh, lc, hc, ll)]
    r = xt.dual_thrust(O, H, L, C, 5, k1, k2)
    same(r.buy_trigger, o + k1 * np.array(rng))
    same(r.sell_trigger, o - k2 * np.array(rng))
    sell_rng = [a - b if a - b >= x - y else x - y for a, b, x, y in zip(hh, lc, hc, ll)]
    hh, hc, lc, ll = hl(14)
    buy_rng = [a - b if a - b >= x - y else x - y for a, b, x, y in zip(hh, lc, hc, ll)]
    r = xt.dual_thrust(O, H, L, C, 14, k1, k2, sell_length=5)
    same(r.buy_trigger[15:], (o + k1 * np.array(buy_rng))[15:])
    same(r.sell_trigger[15:], (o - k2 * np.array(sell_rng))[15:])


def test_standard_error_bands_vs_capissimo_narrow():
    per, mult, sdeg = 20, 2.0, 3
    bi = np.arange(N, dtype=float)
    beta = (p_sum(bi * c, per) - per * p_sma(bi, per) * p_sma(c, per)) / (p_sum(bi ** 2, per) - per * p_sma(bi, per) ** 2)
    alpha = p_sma(c, per) - beta * p_sma(bi, per)
    lr = ti.lsma(C, per).to_numpy()
    val1 = p_sum(c ** 2, per) - alpha * p_sum(c, per) - beta * p_sum(bi * c, per)
    narrow = np.sqrt(val1 / (per - 2))
    r = xt.standard_error_bands(C, per, mult, sdeg)
    same(r.see, narrow, rtol=1e-5)  # the copy's formula loses digits with bar_index as x
    same(r.middle, p_sma(lr, sdeg))
    same(r.upper, p_sma(lr + mult * narrow, sdeg), rtol=1e-8)
    wide = np.sqrt(p_sum((lr - c) ** 2, per) / (per - 2))
    m = ~np.isnan(wide)
    assert not np.allclose(wide[m], narrow[m], rtol=0.05)


def test_adaptive_trend_flow_quantalgo():
    n, sm, sens = 10, 14, 2.0
    t = (H + L + C) / 3
    basis = ((ti.ema(t, n) + ti.ema(t, 2 * n)) / 2).to_numpy()
    sv = ti.ema(pd.Series(p_stdev(t.to_numpy(), n)), sm).to_numpy()
    up, lo = basis + sv * sens, basis - sv * sens
    prev_level, trend = nan, 0
    TR, LV = [], []
    for i in range(N):
        if na(prev_level):
            trend = 1 if c[i] > basis[i] else -1
            prev_level = lo[i] if trend == 1 else up[i]
        if trend == 1:
            if c[i] < lo[i]:
                trend, prev_level = -1, up[i]
            else:
                prev_level = lo[i]
        else:
            if c[i] > up[i]:
                trend, prev_level = 1, lo[i]
            else:
                prev_level = up[i]
        TR.append(trend)
        LV.append(prev_level)
    r = xt.adaptive_trend_flow(H, L, C, n, sm, sens)
    same(r.basis, basis)
    same(r.upper, up)
    same(r.trend, TR)
    same(r.level, LV)


def test_andean_oscillator_alexgrover():
    n, sig = 50, 9
    alpha = 2 / (n + 1)
    up1 = up2 = dn1 = dn2 = nan
    BU, BE = [], []
    for i in range(N):
        C_, O_ = c[i], o[i]
        up1 = nz(pmax(C_, O_, up1 - (up1 - C_) * alpha), C_)
        up2 = nz(pmax(C_ * C_, O_ * O_, up2 - (up2 - C_ * C_) * alpha), C_ * C_)
        dn1 = nz(pmin(C_, O_, dn1 + (C_ - dn1) * alpha), C_)
        dn2 = nz(pmin(C_ * C_, O_ * O_, dn2 + (C_ * C_ - dn2) * alpha), C_ * C_)
        BU.append(math.sqrt(dn2 - dn1 * dn1) if dn2 - dn1 * dn1 >= 0 else nan)
        BE.append(math.sqrt(up2 - up1 * up1) if up2 - up1 * up1 >= 0 else nan)
    r = xt.andean_oscillator(O, C, n, sig)
    same(r.bull, BU)
    same(r.bear, BE)
    same(r.signal, ti.ema(pd.Series(np.maximum(BU, BE)), sig))


@pytest.mark.parametrize("method", ["atr", "manual"])
def test_fib_progression_breaks_luxalgo(method):
    size, mx = (1.0, 3) if method == "atr" else (0.5, 3)
    fib = [1, 1]
    for i in range(1, mx + 1):
        fib.append(fib[i - 1] + fib[i])
    atr = ATR[200]
    avg, fib_n, os_ = 0.0, 1, 0
    AV, OS, TP, SL = [], [], [], []
    for i in range(N):
        dist = (atr[i] if method == "atr" else 1.0) * size * fib[fib_n]
        fib_n = fib_n + 1 if abs(c[i] - avg) > dist else fib_n
        avg = nz(c[i] if fib_n > mx + 1 else at(AV, i - 1), c[i])
        fib_n = 1 if fib_n > mx + 1 else fib_n
        a1 = at(AV, i - 1)
        os_ = 1 if avg > a1 else 0 if avg < a1 else os_
        TP.append(nan if ne(avg, a1) else (avg + dist if os_ == 1 else avg - dist))
        SL.append(nan if ne(avg, a1) else (avg + dist if os_ == 0 else avg - dist))
        AV.append(avg)
        OS.append(os_)
    r = xt.fib_progression_breaks(H, L, C, method, size, mx)
    same(r.avg, AV)
    same(r.os, OS)
    same(r.target, TP)
    same(r.stop, SL)
    assert r.buy.sum() > 3 and r.sell.sum() > 3


def _superichi_avg_port(n, mult):
    atr = ti.atr(H, L, C, n).to_numpy() * mult
    hl2 = (h + l) / 2
    UP, LO, OS, MX, MN, SPT, OUT = [], [], [], [], [], [], []
    for i in range(N):
        s, s1 = c[i], at(c, i - 1)
        up, dn = hl2[i] + atr[i], hl2[i] - atr[i]
        upper = pmin(up, at(UP, i - 1)) if s1 < at(UP, i - 1) else up
        lower = pmax(dn, at(LO, i - 1)) if s1 > at(LO, i - 1) else dn
        os_ = 1 if s > upper else 0 if s < lower else at(OS, i - 1)
        spt = lower if os_ == 1 else upper
        cross = (s > spt and s1 <= at(SPT, i - 1)) or (s < spt and s1 >= at(SPT, i - 1))
        mx = pmax(s, at(MX, i - 1)) if cross else pmax(s, at(MX, i - 1)) if os_ == 1 else spt
        mn = pmin(s, at(MN, i - 1)) if cross else pmin(s, at(MN, i - 1)) if os_ == 0 else spt
        UP.append(upper)
        LO.append(lower)
        OS.append(os_)
        MX.append(mx)
        MN.append(mn)
        SPT.append(spt)
        OUT.append((mx + mn) / 2)
    return np.array(OUT)


def test_superichi_luxalgo():
    ten, kij, sb = _superichi_avg_port(9, 2.0), _superichi_avg_port(26, 4.0), _superichi_avg_port(52, 6.0)
    r = xt.superichi(H, L, C)
    same(r.tenkan, ten)
    same(r.kijun, kij)
    same(r.senkou_b, sb)
    same(r.senkou_a, (kij + ten) / 2)
    same(r.cloud_a, pd.Series((kij + ten) / 2).shift(25))
    same(r.cloud_b, pd.Series(sb).shift(25))


def test_ama_channel_cs_port():
    snrf, p, beta = 2.1, 5, 2.1
    fast = p / 2
    lam = p / fast
    an = lam * (p - 1) / (p - lam)
    pi2 = 1.5707963267948966
    AMA, DMX, DMN, BHB, BLB, HB, LB, NAT, AV1, AL = ([] for _ in range(10))
    for i in range(N):
        x = c[i]
        al1 = at(AL, i - 1)
        ama = al1 * x + (1 - al1) * nz(at(AMA, i - 1))
        ret = (x - at(c, i - 1)) / at(c, i - 1)
        dmx = al1 * pmax(ret, 0) + (1 - al1) * nz(at(DMX, i - 1))
        dmn = -al1 * pmin(ret, 0) + (1 - al1) * nz(at(DMN, i - 1))
        bhb, blb = beta * dmx, beta * dmn
        hb = (1 + at(BHB, i - 1)) * ama
        lb = (1 - at(BLB, i - 1)) * ama
        a1 = at(AMA, i - 1)
        if x > hb:
            snr = ((x - a1) / a1) / blb if blb and a1 else nan
        elif x < lb:
            snr = -((x - a1) / a1) / bhb if bhb and a1 else nan
        else:
            snr = 0
        nat = (math.atan(snrf * snr) + pi2) / (2 * pi2)
        NAT.append(nat)
        av1 = p_wma(NAT[-p:], p)[-1] if i >= p - 1 else nan
        AV1.append(av1)
        f = int(fast)
        av2 = p_wma(AV1[-f:], f)[-1] if i >= f - 1 else nan
        AL.append((1 + an) * av1 - an * av2)
        for lst, val in ((AMA, ama), (DMX, dmx), (DMN, dmn), (BHB, bhb), (BLB, blb), (HB, hb), (LB, lb)):
            lst.append(val)
    r = xt.ama_channel(C, snrf, p, beta)
    same(r.ama, AMA)
    same(r.upper, HB)
    same(r.lower, LB)
    same(r.alpha, AL)


def _custom_hi(x, i, n):
    m = x[i]
    for j in range(0, min(n, 4999) + 1):
        if i - j >= 0 and x[i - j] > m:
            m = x[i - j]
    return m


def _custom_lo(x, i, n):
    m = x[i]
    for j in range(0, min(n, 4999) + 1):
        if i - j >= 0 and x[i - j] < m:
            m = x[i - j]
    return m


def _custom_wma(x, i, n):
    if i - n + 1 < 0:
        return nan
    return sum(x[i - j] * (n - j) for j in range(n)) / (n * (n + 1) / 2)


@pytest.mark.parametrize("series_length", [False, True])
def test_trend_persistence_vawsi_port(series_length):
    sm = 3
    lens = (10 + (np.arange(N) // 37) % 15) if series_length else np.full(N, 14)
    TU, TD_, MX, TR = [], [], [], []
    cum_u = cum_d = nan
    up = dn = nan
    out = []
    for i in range(N):
        n = int(lens[i])
        TU.append(abs(c[i] - _custom_hi(c, i, n)))
        TD_.append(abs(c[i] - _custom_lo(c, i, n)))
        wu, wd = _custom_wma(TU, i, sm), _custom_wma(TD_, i, sm)
        pu, pdn = cum_u, cum_d
        if not na(wu):
            cum_u = wu if na(cum_u) else cum_u + wu
        if not na(wd):
            cum_d = wd if na(cum_d) else cum_d + wd
        MX.append(pmax(cum_u - pu, cum_d - pdn))
        TR.append(_custom_wma(MX, i, sm))
        ch = TR[i] - at(TR, i - 1)
        up = nz(up) * (n - 1) / n + pmax(ch, 0) / n
        dn = nz(dn) * (n - 1) / n + (-pmin(ch, 0)) / n
        out.append(100 - 100 / (1 + up / dn) if dn != 0 else nan)
    ln = pd.Series(lens.astype(float), index=C.index)
    same(xt.trend_persistence(C, ln, sm), out)


def test_rsi_trend_threshold_port():
    n, mult, sltp = 8, 1.5, 10.0
    src = ti.ohlc4(O, H, L, C).to_numpy()  # Heikin-Ashi close
    rsi = ti.rsi(pd.Series(src), n).to_numpy()
    atr = ATR[8]
    sl, tp = (100 - sltp) / 100, (100 + sltp) / 100
    xu = xd = False
    last, bear, d, th = None, 0, nan, nan
    X1, Y1, X2, Z2, TH, DR = [], [], [], [], [], []
    for i in range(N):
        if xu or xd:
            last = i
        bear = bear + 1 if last is None else i - last
        rl, ru, an = rsi[i], abs(rsi[i] - 100), atr[i] / src[i]
        X1.append(_custom_hi(src, i, bear) * (1 - (an + (1 / rl * mult if rl else nan))))
        Y1.append(pmax(_custom_hi(X1, i, bear), src[i] * sl))
        lower = _custom_hi(Y1, i, bear)
        X2.append(_custom_lo(src, i, bear) * (1 + (an + (1 / ru * mult if ru else nan))))
        Z2.append(pmin(_custom_lo(X2, i, bear), src[i] * tp))
        upper = _custom_lo(Z2, i, bear)
        prev = th
        if na(th):
            th = lower
        if na(d):
            d = 1
        if xd:
            d = -1
        if xu:
            d = 1
        if d == 1:
            th = lower
        if d == -1:
            th = upper
        xu = src[i] > th and at(src, i - 1) <= prev
        xd = src[i] < th and at(src, i - 1) >= prev
        TH.append(th)
        DR.append(d)
    r = xt.rsi_trend_threshold(pd.Series(src, index=C.index), H, L, C, n, mult, sltp)
    same(r.threshold, TH)
    same(r.direction, DR)
    assert (np.diff(DR) != 0).sum() > 10


def test_range_filter_trailing_band_port():
    def smoothrng(t, m):
        avrng = ti.ema(pd.Series(np.abs(np.diff(c, prepend=nan))), t)
        return ti.ema(avrng, t * 2 - 1).to_numpy() * m

    smrng = (smoothrng(27, 1.6) + smoothrng(55, 2.0)) / 2
    F = []
    for i in range(N):
        x, r_, p = c[i], smrng[i], nz(at(F, i - 1))
        F.append((p if x - r_ < p else x - r_) if x > p else (p if x + r_ > p else x + r_))
    F = np.array(F)
    STR, STS = F + smrng, F - smrng
    FUB, FLB, TRF = [], [], []
    for i in range(N):
        pf, pl_ = nz(at(FUB, i - 1)), nz(at(FLB, i - 1))
        FUB.append(STR[i] if STR[i] < pf or at(c, i - 1) > pf else pf)
        FLB.append(STS[i] if STS[i] > pl_ or at(c, i - 1) < pl_ else pl_)
        pt, f1, l1 = nz(at(TRF, i - 1)), at(FUB, i - 1), at(FLB, i - 1)
        fub, flb = FUB[i], FLB[i]
        TRF.append(fub if pt == f1 and c[i] <= fub else flb if pt == f1 and c[i] >= fub else
                   flb if pt == l1 and c[i] >= flb else fub if pt == l1 and c[i] <= flb else fub)
    r = xt.range_filter_trailing(C)
    same(r.filter, F)
    same(r.upper, FUB)
    same(r.lower, FLB)
    same(r.trail, TRF)


def test_trend_thrust_indicator_tasc():
    f = ti.vwma(C, V, 13).to_numpy()
    s = ti.vwma(C, V, 26).to_numpy()
    vm = (f / s) ** 2
    tti = f * vm - s / vm
    r = xt.trend_thrust_indicator(C, V)
    same(r.tti, tti)
    same(r.signal, p_sma(tti, 9))


# ---------------------------------------------------------------------------
# Library behaviour
# ---------------------------------------------------------------------------

_ARGS = {"open": O, "high": H, "low": L, "close": C, "volume": V, "source": C, "y": C, "x": V, "mavg": C,
         "atr": H - L, "length": 14}


@pytest.mark.parametrize("name", sorted(xt.EXTRA_TREND))
def test_no_lookahead(name):
    """Values up to bar t do not change when later bars are removed."""
    fn = xt.EXTRA_TREND[name]
    cut = 2000
    full = fn(**{i: _ARGS[i] for i in fn.inputs})
    part = fn(**{i: (_ARGS[i].iloc[:cut] if hasattr(_ARGS[i], "iloc") else _ARGS[i]) for i in fn.inputs})
    full = full if isinstance(full, tuple) else (full,)
    part = part if isinstance(part, tuple) else (part,)
    for a, b in zip(full, part):
        same(np.asarray(a, float)[:cut], np.asarray(b, float))


def test_registry_is_separate():
    assert set(xt.EXTRA_TREND).isdisjoint(ti._core.REGISTRY)
    assert len(xt.__all__) == len(xt.EXTRA_TREND)
    df = pd.DataFrame({"a": C, "b": C * 1.1})
    r = xt.g_channel(df, 50)
    same(r.upper["b"], xt.g_channel(C * 1.1, 50).upper)
