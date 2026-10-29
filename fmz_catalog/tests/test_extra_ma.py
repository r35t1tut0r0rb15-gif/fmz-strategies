"""Tests for fmz_catalog/extra_ma.py.

Each indicator is compared with a literal bar-by-bar Python port of the Pine
code it comes from (the strategy copy, or the original script where the copy
is buggy). The ports use plain Python floats and lists and none of the
library's kernels, and follow Pine's rules: ``x[n]`` is ``na`` before bar n,
``nz()``, comparisons with ``na`` are false, ``ta.*`` windows are ``na``
while they hold an ``na``, ``ta.ema``/``ta.rma`` seed with an SMA.
"""

import math

import numpy as np
import pandas as pd
import pytest

import fmz_catalog.extra_ma as xm
from tv_indicators.tests.test_indicators import C, H, L, N, O, V, c, h, l, o, same, v
from tv_indicators.volume import session_ids

NA = math.nan


# ---------------------------------------------------------------------------
# Pine helpers (plain Python)
# ---------------------------------------------------------------------------

def na(x):
    return x is None or (isinstance(x, float) and math.isnan(x))


def nz(x, r=0.0):
    return r if na(x) else x


def at(a, i, n=0):
    """``a[n]`` on bar i."""
    j = i - n
    return a[j] if 0 <= j < len(a) else NA


def pmax(a, b):
    return NA if na(a) or na(b) else max(a, b)


def pmin(a, b):
    return NA if na(a) or na(b) else min(a, b)


def div(a, b):
    if na(a) or na(b) or b == 0:
        return NA
    return a / b


def window(x, i, n):
    if i < n - 1:
        return None
    w = x[i - n + 1:i + 1]
    return None if any(na(t) for t in w) else w


def p_sum(x, n):
    out = []
    for i in range(len(x)):
        w = window(x, i, n)
        out.append(NA if w is None else sum(w))
    return out


def p_sma(x, n):
    return [s / n if not na(s) else NA for s in p_sum(x, n)]


def p_wma(x, n):
    out = []
    for i in range(len(x)):
        if i < n - 1:
            out.append(NA)
            continue
        s = 0.0
        for j in range(n):
            s += x[i - j] * (n - j)
        out.append(s / (n * (n + 1) / 2))
    return out


def wma_last(x, n):
    """``ta.wma(x, n)`` on the last bar of list x."""
    i = len(x) - 1
    if i < n - 1:
        return NA
    return sum(x[i - j] * (n - j) for j in range(n)) / (n * (n + 1) / 2)


def sma_last(x, n):
    w = window(x, len(x) - 1, n)
    return NA if w is None else sum(w) / n


def p_ewm(x, n, a):
    out, st, cnt, acc = [], NA, 0, 0.0
    for t in x:
        if not na(t):
            if cnt < n:
                acc += t
                cnt += 1
                if cnt == n:
                    st = acc / n
            else:
                st = a * t + (1 - a) * st
        out.append(st)
    return out


def p_ema(x, n):
    return p_ewm(x, n, 2 / (n + 1))


def p_rma(x, n):
    return p_ewm(x, n, 1 / n)


def p_highest(x, n):
    return [NA if window(x, i, n) is None else max(window(x, i, n)) for i in range(len(x))]


def p_lowest(x, n):
    return [NA if window(x, i, n) is None else min(window(x, i, n)) for i in range(len(x))]


def p_stdev(x, n):
    out = []
    for i in range(len(x)):
        w = window(x, i, n)
        if w is None:
            out.append(NA)
            continue
        m = sum(w) / n
        out.append(math.sqrt(sum((t - m) ** 2 for t in w) / n))
    return out


def p_tr(hh, ll, cc):
    out = []
    for i in range(len(cc)):
        if i == 0:
            out.append(hh[0] - ll[0])
        else:
            out.append(max(hh[i] - ll[i], abs(hh[i] - cc[i - 1]), abs(ll[i] - cc[i - 1])))
    return out


def p_atr(hh, ll, cc, n):
    return p_rma(p_tr(hh, ll, cc), n)


def pround(x):
    return math.floor(x + 0.5) if x >= 0 else -math.floor(-x + 0.5)


def p_cross(a, b, a1, b1):
    over = a > b and a1 <= b1
    under = a < b and a1 >= b1
    return over or under


cl, hi, lo, op, vo = (list(map(float, x)) for x in (c, h, l, o, v))


def lin(x):
    return [float(t) for t in x]


# ---------------------------------------------------------------------------
# Volume-weighted averages
# ---------------------------------------------------------------------------

def test_evwma_quantnomad_and_lazybear():
    n = 30
    vp = p_sum(vo, n)
    out, prev = [], NA
    for i in range(N):  # QuantNomad EVWBB: nz(evwma[1], close)
        e = div((vp[i] - vo[i]) * nz(prev, cl[i]) + vo[i] * cl[i], vp[i])
        out.append(e)
        prev = e
    same(xm.evwma(C, V, n), out)
    lb, prev = [], NA
    for i in range(N):  # LazyBear: nz(data[1]) * (nb - v)/nb + v*p/nb
        e = NA if na(vp[i]) else nz(prev) * (vp[i] - vo[i]) / vp[i] + (vo[i] * cl[i] / vp[i])
        lb.append(e)
        prev = e
    same(xm.evwma(C, V, n, seed="zero"), lb)
    cum, out2, prev = 0.0, [], NA
    for i in range(N):
        cum += vo[i]
        e = ((cum - vo[i]) * nz(prev, cl[i]) + vo[i] * cl[i]) / cum
        out2.append(e)
        prev = e
    same(xm.evwma(C, V, n, cumulative=True), out2)


def test_vwema():
    n = 20
    same(xm.vwema(C, V, n), np.array(p_ema([a * b for a, b in zip(cl, vo)], n)) / np.array(p_ema(vo, n)))


@pytest.mark.parametrize("include", [False, True])
def test_session_vwma(include):
    sid = session_ids(C.index, "D")
    ln = 55
    out, bs = [], NA
    for i in range(N):
        new = i > 0 and sid[i] - sid[i - 1] != 0
        bs = 0 if new else (bs + 1 if not na(bs) else NA)
        if na(bs):
            vl = ln
        elif include:
            vl = min(bs + 1, ln)
        else:
            vl = max(1, bs if bs < ln else ln)
        if i < vl - 1:
            out.append(NA)
            continue
        sp = sum(cl[i - j] * vo[i - j] for j in range(vl)) / vl
        sv = sum(vo[i - j] for j in range(vl)) / vl
        out.append(sp / sv)
    same(xm.session_vwma(C, V, pd.Series(sid, index=C.index), ln, include_session_open=include), out)


def test_vawma_vawsi():
    n = 14
    atr = p_tr(hi, lo, cl)
    aavg = [s / n if not na(s) else NA for s in p_sum(atr, n)]
    vavg = [s / n if not na(s) else NA for s in p_sum(vo, n)]
    out = []
    for i in range(N):
        if i < n:
            out.append(NA)
            continue
        ws = sw = 0.0
        for j in range(n + 1):
            w = (vo[i - j] / vavg[i] + atr[i - j] / aavg[i]) / 2
            ws += cl[i - j] * w
            sw += w
        out.append(ws / sw)
    same(xm.vawma(C, H, L, V, n), out)


# ---------------------------------------------------------------------------
# Angle, Kalman
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("lookback,per_bar", [(1, False), (2, True), (8, False)])
def test_ma_angle_atr(lookback, per_bar):
    src = p_sma(cl, 21)
    atr = p_atr(hi, lo, cl, 10)
    rad2degree = 180 / 3.141592653589793238462643
    out = []
    for i in range(N):
        r = div(src[i] - at(src, i, lookback), atr[i])
        if per_bar and not na(r):
            r = r / lookback
        out.append(NA if na(r) else rad2degree * math.atan(r))
    same(xm.ma_angle_atr(pd.Series(src, index=C.index), H, L, C, lookback, 10, per_bar), out)


@pytest.mark.parametrize("variant", ["brahmastra", "loft", "transitive"])
def test_kalman_ports(variant):
    kf, velo, out, vel = NA, NA, [], []
    for i in range(N):
        x = cl[i]
        if variant == "brahmastra":   # kahlman(x, g): sqrt(g*2), g*dk
            g = 0.7
            dk = x - nz(kf, x)
            smooth = nz(kf, x) + dk * math.sqrt(g * 2)
            velo = nz(velo, 0) + (g * dk)
        elif variant == "loft":       # gain / 10000
            gain = 200.0
            dk = x - nz(kf, x)
            smooth = nz(kf, x) + dk * math.sqrt(gain / 10000 * 2)
            velo = nz(velo, 0) + gain / 10000 * dk
        else:                         # Distance*K/100, sqrt(Sharpness*K/100)
            sharp, kk = 1.0, 1.0
            dk = x - nz(kf, x)
            smooth = nz(kf, x) + dk * math.sqrt(sharp * kk / 100)
            velo = nz(velo, 0) + dk * kk / 100
        kf = smooth + velo
        out.append(kf)
        vel.append(velo)
    r = {"brahmastra": xm.kalman_alpha_beta(C, 0.7),
         "loft": xm.kalman_alpha_beta(C, 200, scale=10000),
         "transitive": xm.kalman_alpha_beta(C, 1.0, scale=100, sharpness=1.0)}[variant]
    same(r.kalman, out, rtol=1e-8)
    same(r.velocity, vel, rtol=1e-8, atol=1e-9)


# ---------------------------------------------------------------------------
# SSL Hybrid selector
# ---------------------------------------------------------------------------

def _ssf2(x, length):
    pi = 2 * math.asin(1)
    arg = math.sqrt(2) * pi / length
    a1 = math.exp(-arg)
    b1 = 2 * a1 * math.cos(arg)
    c2, c3 = b1, -math.pow(a1, 2)
    c1 = 1 - c2 - c3
    out = []
    for i in range(len(x)):
        out.append(c1 * x[i] + c2 * nz(at(out, i, 1)) + c3 * nz(at(out, i, 2)))
    return out


def _ssf3(x, length):
    pi = 2 * math.asin(1)
    arg = pi / length
    a1 = math.exp(-arg)
    b1 = 2 * a1 * math.cos(1.738 * arg)
    c1 = math.pow(a1, 2)
    coef2, coef3, coef4 = b1 + c1, -(c1 + b1 * c1), math.pow(c1, 2)
    coef1 = 1 - coef2 - coef3 - coef4
    out = []
    for i in range(len(x)):
        out.append(coef1 * x[i] + coef2 * nz(at(out, i, 1)) + coef3 * nz(at(out, i, 2))
                   + coef4 * nz(at(out, i, 3)))
    return out


def _edsma_port(src, length, ssf_length, poles):
    zeros = [src[i] - nz(at(src, i, 2)) for i in range(len(src))]
    avg = [(zeros[i] + at(zeros, i, 1)) / 2 for i in range(len(src))]
    ssf = _ssf2(avg, ssf_length) if poles == 2 else _ssf3(avg, ssf_length)
    sd = p_stdev(ssf, length)
    out, e = [], NA
    for i in range(len(src)):
        scaled = ssf[i] / sd[i] if (not na(sd[i]) and sd[i] != 0) else 0
        alpha = 5 * abs(scaled) / length
        e = alpha * src[i] + (1 - alpha) * nz(e)
        out.append(e)
    return out, sd


def _hma(x, n):
    a = p_wma(x, int(n / 2))
    b = p_wma(x, n)
    return p_wma([2 * p - q for p, q in zip(a, b)], int(pround(math.sqrt(n))))


def _ssl_ma(t, src, ln, kidiv=1, jphase=3, jpower=1, vlb=10, beta_mf=0.8, feedback=False, z=0.5):
    n = len(src)
    if t == "TMA":
        return p_sma(p_sma(src, math.ceil(ln / 2)), math.floor(ln / 2) + 1)
    if t == "MF":
        alpha = 2 / (ln + 1)
        ts, b, cc, os_ = [], [], [], []
        for i in range(n):
            a = z * src[i] + (1 - z) * nz(at(ts, i, 1), src[i]) if feedback else src[i]
            e = alpha * a + (1 - alpha) * nz(at(b, i, 1), a)
            b.append(a if a > e else e)
            e2 = alpha * a + (1 - alpha) * nz(at(cc, i, 1), a)
            cc.append(a if a < e2 else e2)
            os_.append(1 if a == b[i] else 0 if a == cc[i] else at(os_, i, 1))
            upper = beta_mf * b[i] + (1 - beta_mf) * cc[i]
            lower = beta_mf * cc[i] + (1 - beta_mf) * b[i]
            ts.append(os_[i] * upper + (1 - os_[i]) * lower)
        return ts
    if t == "LSMA":
        out = []
        for i in range(n):
            w = window(src, i, ln)
            if w is None:
                out.append(NA)
                continue
            xs = list(range(ln))
            mx, my = sum(xs) / ln, sum(w) / ln
            sl = sum((a - mx) * (bb - my) for a, bb in zip(xs, w)) / sum((a - mx) ** 2 for a in xs)
            out.append(my + sl * (ln - 1 - mx))
        return out
    if t == "SMA":
        return p_sma(src, ln)
    if t == "EMA":
        return p_ema(src, ln)
    if t == "DEMA":
        e = p_ema(src, ln)
        return [2 * a - b for a, b in zip(e, p_ema(e, ln))]
    if t == "TEMA":
        e = p_ema(src, ln)
        e2 = p_ema(e, ln)
        return [3 * (a - b) + d for a, b, d in zip(e, e2, p_ema(e2, ln))]
    if t == "WMA":
        return p_wma(src, ln)
    if t == "VAMA":
        mid = p_ema(src, ln)
        dev = [a - b for a, b in zip(src, mid)]
        return [m + (u + d) / 2 for m, u, d in zip(mid, p_highest(dev, vlb), p_lowest(dev, vlb))]
    if t == "HMA":
        return _hma(src, ln)
    if t == "JMA":
        pr = 0.5 if jphase < -100 else 2.5 if jphase > 100 else jphase / 100 + 1.5
        beta = 0.45 * (ln - 1) / (0.45 * (ln - 1) + 2)
        alpha = math.pow(beta, jpower)
        e0 = e1 = e2 = jma = NA
        out = []
        for i in range(n):
            e0 = (1 - alpha) * src[i] + alpha * nz(e0)
            e1 = (src[i] - e0) * (1 - beta) + beta * nz(e1)
            e2 = (e0 + pr * e1 - nz(jma)) * math.pow(1 - alpha, 2) + math.pow(alpha, 2) * nz(e2)
            jma = e2 + nz(jma)
            out.append(jma)
        return out
    if t == "Kijun v2":
        kij = [(a + b) / 2 for a, b in zip(p_lowest(lo, ln), p_highest(hi, ln))]
        m = int(ln / kidiv)
        conv = [(a + b) / 2 for a, b in zip(p_lowest(lo, m), p_highest(hi, m))]
        return [(a + b) / 2 for a, b in zip(kij, conv)]
    if t == "McGinley":
        ema = p_ema(src, ln)  # only called while mg[1] is na, i.e. on the first bars
        out, mg = [], NA
        for i in range(n):
            mg = ema[i] if na(mg) else mg + (src[i] - mg) / (ln * math.pow(src[i] / mg, 4))
            out.append(mg)
        return out
    if t == "EDSMA":
        e, sd = _edsma_port(src, ln, 20, 2)
        return e
    raise AssertionError(t)


@pytest.mark.parametrize("t", ["TMA", "MF", "LSMA", "SMA", "EMA", "DEMA", "TEMA", "WMA", "VAMA",
                               "HMA", "JMA", "Kijun v2", "McGinley"])
@pytest.mark.parametrize("ln", [60, 15])
def test_ssl_hybrid_ma(t, ln):
    same(xm.ssl_hybrid_ma(C, H, L, ln, t), _ssl_ma(t, cl, ln), rtol=1e-8, atol=1e-8)


def test_ssl_hybrid_mf_feedback_and_edsma():
    same(xm.ssl_hybrid_ma(C, H, L, 20, "MF", mf_feedback=True),
         _ssl_ma("MF", cl, 20, feedback=True), rtol=1e-9)
    port, sd = _edsma_port(cl, 60, 20, 2)
    port = [NA if na(s) else e for e, s in zip(port, sd)]  # script prints 0 there
    same(xm.ssl_hybrid_ma(C, H, L, 60, "EDSMA"), port, rtol=1e-8)


@pytest.mark.parametrize("poles", [2, 3])
def test_edsma_everget(poles):
    port, sd = _edsma_port(cl, 40, 20, poles)
    assert all(e == 0 for e, s in zip(port, sd) if na(s))  # the script's warm-up zeros
    same(xm.edsma(C, 40, 20, poles), [NA if na(s) else e for e, s in zip(port, sd)], rtol=1e-8)


# ---------------------------------------------------------------------------
# Fixed-weight windows
# ---------------------------------------------------------------------------

def test_sine_wma_everget_and_insilico_copy():
    n = 14
    pi = 2 * math.asin(1)
    ev, cp = [], []
    for i in range(N):
        s = ws = s2 = ws2 = 0.0
        for j in range(n):
            w = math.sin((j + 1) * pi / (n + 1))     # everget
            s += nz(at(cl, i, j)) * w
            ws += w
            w2 = math.sin(j * pi / (n + 1))          # MA Emperor copy
            s2 += nz(at(cl, i, j)) * w2
            ws2 += w2
        ev.append(s / ws if i >= n - 1 else NA)
        cp.append(s2 / ws2)
    same(xm.sine_wma(C, n), ev)
    same(xm.sine_wma(C, n, insilico_compat=True), cp)
    # the copy ignores the current bar: it equals the everget-style sum of bars 1..n-1
    w = [math.sin(j * pi / (n + 1)) for j in range(1, n)]
    lagged = sum(w[j - 1] * c[200 - j] for j in range(1, n)) / sum(w)
    assert cp[200] == pytest.approx(lagged, rel=1e-12)


@pytest.mark.parametrize("terms", [7, 8, 15])
def test_henderson_everget(terms):
    def get_weight(m, j):
        num = 315 * (math.pow(m + 1, 2) - math.pow(j, 2)) * (math.pow(m + 2, 2) - math.pow(j, 2)) \
            * (math.pow(m + 3, 2) - math.pow(j, 2)) * (3 * math.pow(m + 2, 2) - 11 * math.pow(j, 2) - 16)
        den = 8 * (m + 2) * (math.pow(m + 2, 2) - 1) * (4 * math.pow(m + 2, 2) - 1) \
            * (4 * math.pow(m + 2, 2) - 9) * (4 * math.pow(m + 2, 2) - 25)
        return num / den if den != 0 else 0

    out = []
    tm = (terms - 1) / 2
    for i in range(N):
        s = ws = 0.0
        for j in range(terms):
            w = get_weight(tm, j - tm)
            s += nz(at(cl, i, j)) * w
            ws += w
        out.append(s / ws if i >= terms - 1 else NA)
    same(xm.henderson_ma(C, terms), out)
    if terms % 2:  # odd-length Henderson weights sum to 1 (known property)
        assert sum(get_weight(tm, j - tm) for j in range(terms)) == pytest.approx(1.0)


def test_retro_quadratic_windowed():
    n = 20
    wx = 100 / (4 + (n - 4) * 1.30)
    wy = 1.30 * wx
    rw, qw, we, wj = [], [], [], []
    sc = 2.0 / (n + 1)
    for i in range(N):
        if i < n - 1:
            for lst in (rw, qw, we, wj):
                lst.append(NA)
            continue
        s = d = 0.0
        s2 = d2 = 0.0
        s3 = d3 = 0.0
        s4 = d4 = 0.0
        for j in range(n):
            w = wx if j <= 3 else wy
            s += cl[i - j] * w
            d += w
            w2 = (n - j) * (n - j)
            s2 += cl[i - j] * w2
            d2 += w2
            w3 = math.pow(1 - sc, j)
            s3 += cl[i - j] * w3
            d3 += w3
            w4 = (1 - 0.5) * math.pow(0.5, j)
            s4 += w4 * cl[i - j]
            d4 += w4
        rw.append(s / d)
        qw.append(s2 / d2)
        we.append(s3 / d3)
        wj.append(s4 / d4)
    same(xm.retro_wma(C, n), rw)
    same(xm.quadratic_wma(C, n), qw)
    same(xm.windowed_ema(C, n), we)
    same(xm.windowed_ema(C, n, 0.5), wj)


@pytest.mark.parametrize("n", [5, 10, 30])
def test_binomial_ma(n):
    fac = math.factorial  # exact; Pine's int factorial overflows for 2n-1 >= 21
    cof = [0.0] * n
    cof[n - 1] = 1
    tot = 1.0
    for i in range(2, n + 1):
        cof[n - i] = fac(2 * n - 1) / (fac(i - 1) * fac(2 * n - i))
        tot += cof[n - i]
    w = [x / tot for x in cof]
    out = [sum(w[j] * cl[i - j] for j in range(n)) if i >= n - 1 else NA for i in range(N)]
    same(xm.binomial_ma(C, n), out)


def test_geometric_mean_after_warmup():
    per = 20
    out = []
    for i in range(N):
        g = math.pow(cl[i], 1.0 / per)
        for j in range(1, per):
            g *= math.pow(at(cl, i, j), 1.0 / per)
        out.append(g if i > per else cl[i])   # ggx = n > per ? gx : price
    r = xm.geometric_mean_ma(C, per).to_numpy()
    same(r[per + 1:], out[per + 1:], rtol=1e-12)
    assert np.isnan(r[:per - 1]).all() and not np.isnan(r[per - 1:]).any()


def test_signed_wma():
    y = 5
    out = []
    for i in range(N):
        if i < y - 1:
            out.append(NA)
            continue
        nrm = s = 0.0
        for j in range(y):
            w = (y - j) * y
            nrm += w
            f = -1 if cl[i - j] < op[i - j] else 1
            s += vo[i - j] * w * f
        out.append(s / nrm)
    same(xm.signed_wma(V, O, C, y), out)


# ---------------------------------------------------------------------------
# Kernels
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("kernel", ["beta", "gaussian", "epanechnikov"])
def test_kernel_ma_b4100(kernel):
    n, a, b, bw = 20, 3.0, 3.0, 0.3
    kern, s = [], 0.0
    for i in range(n):
        x = i / (n - 1)
        if kernel == "beta":
            w = math.pow(x, a - 1) * math.pow(1 - x, b - 1)
        elif kernel == "gaussian":
            w = math.exp(-0.5 * math.pow((x - 0.5) / bw, 2))
        else:
            w = max(0.0, 1 - math.pow((x - 0.5) / bw, 2))
        kern.append(w)
        s += w
    kern = [w / s for w in kern]
    out = []
    for i in range(N):
        if i < n - 1:
            out.append(NA)
            continue
        acc = 0.0
        for j in range(n):
            acc += cl[i - j] * kern[j]
        out.append(acc)
    same(xm.kernel_ma(C, n, kernel, a, b, bw), out)


def test_multi_kernel_regression():
    reg, h1, h2, al = 30, 5.0, 5.0, 0.5
    g_out, e_out, m_out = [], [], []
    for i in range(N):
        if i < reg - 1:
            g_out.append(NA)
            e_out.append(NA)
            m_out.append(NA)
            continue
        num = den = 0.0
        for j in range(reg):
            w = math.exp(-0.5 * math.pow(j / h1, 2))
            num += cl[i - j] * w
            den += w
        g = num / (1 if den == 0 else den)
        num = den = 0.0
        for j in range(reg):
            r = j / h2
            w = (1 - math.pow(r, 2)) if abs(r) <= 1 else 0
            num += cl[i - j] * w
            den += w
        e = num / (1 if den == 0 else den)
        g_out.append(g)
        e_out.append(e)
        m_out.append(al * g + (1 - al) * e)
    r = xm.multi_kernel_regression(C, reg, h1, h2, al)
    same(r.gaussian, g_out)
    same(r.epanechnikov, e_out)
    same(r.mkr, m_out)


def _cp_gaussian_kernel(src, size, hh, r):
    def gaussian(x, bw):
        return math.exp(-math.pow(x / bw, 2) / 2) / math.sqrt(2 * math.pi)

    out = []
    for i in range(len(src)):
        wt = ws = 0.0
        for j in range(size + 1):
            s = at(src, i, j)
            kk = math.pow(j, 2) / (math.pow(hh, 2) * r)
            w = gaussian(kk, r)
            wt += s * w
            ws += w
        out.append(wt / ws)
    return out


def _chebyshev(src, ln, ripple):
    def cosh(x):
        return (math.exp(x) + math.exp(-x)) / 2

    def acosh(x):
        return NA if x < 1 else math.log(x + math.sqrt(x * x - 1))

    def sinh(x):
        return (math.exp(x) - math.exp(-x)) / 2

    def asinh(x):
        return math.log(x + math.sqrt(x * x + 1))

    a = cosh(1 / ln * acosh(1 / (1 - ripple)))
    b = sinh(1 / ln * asinh(1 / ripple))
    cc = (a - b) / (a + b)
    out, ch = [], NA
    for s in src:
        ch = (1 - cc) * s + cc * nz(ch)
        out.append(ch)
    return out


def test_chartprime_chebyshev_and_gaussian_kernel():
    same(xm.chebyshev_ma(C, 8, 0.05), _chebyshev(cl, 8, 0.05))
    same(xm.kernel_regression_chartprime(C, 64, 4, 0.5), _cp_gaussian_kernel(cl, 64, 4, 0.5))
    # smoothing(source, 3, extra) on the script's donchian average
    don = [(a + b) / 2 for a, b in zip(p_lowest(lo, 9), p_highest(hi, 9))]
    sm = _cp_gaussian_kernel(_chebyshev(don, 3, 0.5), 4, 2, 1)
    same(xm.chebyshev_filter(pd.Series(don, index=C.index), 3, True), sm)
    same(xm.chebyshev_filter(pd.Series(don, index=C.index), 3, False), _chebyshev(don, 3, 0.5))


def test_sine_fir_luxalgo_kaspricci():
    n, al, be = 50, 1.0, 0.5
    b = []
    for i in range(n):
        x = i / (n - 1)
        b.append(math.sin(2 * 3.14159 * math.pow(x, al)) * (1 - math.pow(x, be)))
    out = []
    for i in range(N):
        s = 0.0
        for j in range(n):
            s += at(cl, i, j) * b[j]
        out.append(s / sum(b))
    same(xm.sine_fir_filter(C, n, al, be), out)


def test_gaussian_fir_channel():
    n = 20
    half = (n - 1) / 2.0
    den = (n / 6.0) * (n / 6.0)
    mid, sd = [], []
    for i in range(N):
        if i < n - 1:
            mid.append(NA)
            sd.append(NA)
            continue
        s = nrm = 0.0
        for j in range(n):
            x = j - half
            w = math.exp(-(x * x) / (2 * den))
            s += cl[i - j] * w
            nrm += w
        g = s / nrm
        s = nrm = 0.0
        for j in range(n):
            x = j - half
            w = math.exp(-(x * x) / (2 * den))
            s += (cl[i - j] - g) ** 2 * w
            nrm += w
        mid.append(g)
        sd.append(math.sqrt(s / nrm))
    r = xm.gaussian_fir(C, n)
    same(r.mid, mid)
    same(r.std, sd)


# ---------------------------------------------------------------------------
# Adaptive averages
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("seed", ["zero", "sma"])
def test_vma_lazybear(seed):
    ln = 6
    k_ = 1.0 / ln
    pdmS, mdmS, pdiS, mdiS, iS, vma = [], [], [], [], [], []
    sma = p_sma(cl, ln)
    for i in range(N):
        src, s1_ = cl[i], at(cl, i, 1)
        pdm = pmax(src - s1_, 0) if not na(s1_) else NA
        mdm = pmax(s1_ - src, 0) if not na(s1_) else NA
        pdmS.append((1 - k_) * nz(at(pdmS, i, 1)) + k_ * pdm)
        mdmS.append((1 - k_) * nz(at(mdmS, i, 1)) + k_ * mdm)
        s = pdmS[i] + mdmS[i]
        pdi, mdi = div(pdmS[i], s), div(mdmS[i], s)
        pdiS.append((1 - k_) * nz(at(pdiS, i, 1)) + k_ * pdi)
        mdiS.append((1 - k_) * nz(at(mdiS, i, 1)) + k_ * mdi)
        d = abs(pdiS[i] - mdiS[i])
        s1 = pdiS[i] + mdiS[i]
        iS.append((1 - k_) * nz(at(iS, i, 1)) + div(k_ * d, s1))
        w = window(iS, i, ln)
        vi = NA if w is None else div(iS[i] - min(w), max(w) - min(w))
        prev = at(vma, i, 1)
        if seed == "sma":
            val = sma[i] if na(prev) else k_ * vi * src + (1 - k_ * vi) * nz(prev)
        else:
            val = (1 - k_ * vi) * nz(prev) + k_ * vi * src
        vma.append(val)
    same(xm.vma_lazybear(C, ln, seed), vma, rtol=1e-8)


def test_trama_luxalgo():
    n = 99
    hh_, ll_ = p_highest(hi, n), p_lowest(lo, n)
    flag = []
    for i in range(N):
        ch_h = hh_[i] - at(hh_, i, 1)
        ch_l = ll_[i] - at(ll_, i, 1)
        hh = pmax(np.sign(ch_h), 0) if not na(ch_h) else NA
        ll = pmax(np.sign(ch_l) * -1, 0) if not na(ch_l) else NA
        flag.append(1.0 if (not na(hh) and hh != 0) or (not na(ll) and ll != 0) else 0.0)
    tc = [NA if na(x) else math.pow(x, 2) for x in p_sma(flag, n)]
    out, ama = [], NA
    for i in range(N):
        e = ama + tc[i] * (cl[i] - ama)
        ama = cl[i] if na(e) else e
        out.append(ama)
    same(xm.trama(H, L, C, n), out)


def test_sama_mightyzinger():
    length, mn, mj = 200, 6, 14
    min_a, maj_a = 2 / (mn + 1), 2 / (mj + 1)
    hh, ll = p_highest(hi, length + 1), p_lowest(lo, length + 1)
    out, ama = [], NA
    for i in range(N):
        mult = abs(2 * cl[i] - ll[i] - hh[i]) / (hh[i] - ll[i]) if (not na(hh[i]) and hh[i] - ll[i] != 0) else 0
        fa = math.pow(mult * (min_a - maj_a) + maj_a, 2)
        ama = (cl[i] - nz(ama)) * fa + nz(ama)
        out.append(ama)
    same(xm.slope_adaptive_ma(H, L, C, length, mn, mj), out)


def test_uhl_alexgrover():
    n = 100
    sma = p_sma(cl, n)
    var = [NA if na(s) else s * s for s in p_stdev(cl, n)]
    cma_o, cts_o, cma, cts = [], [], NA, NA
    for i in range(N):
        secma = math.pow(nz(sma[i] - cma), 2)
        sects = math.pow(nz(cl[i] - cts), 2)
        ka = 1 - var[i] / secma if var[i] < secma else 0
        kb = 1 - var[i] / sects if var[i] < sects else 0
        cma = ka * sma[i] + (1 - ka) * nz(cma, cl[i])
        cts = kb * cl[i] + (1 - kb) * nz(cts, cl[i])
        cma_o.append(cma)
        cts_o.append(cts)
    r = xm.uhl_ma(C, n)
    same(r.cma, cma_o, rtol=1e-8)
    same(r.cts, cts_o, rtol=1e-8)


def test_ama_durenard_cryptostatistical():
    lookback, beta, snrfactor = 5, 2.1, 2.1
    price = cl
    pi2 = 1.5707963267948966
    fast = lookback / 2
    lam = lookback / fast
    al_n = lam * (lookback - 1) / (lookback - lam)
    ama, dmax, dmin, bhb, blb, hb, lb, natan, av1, alpha = ([] for _ in range(10))
    for i in range(N):
        a1 = at(alpha, i, 1)
        ama.append(a1 * price[i] + (1 - a1) * nz(at(ama, i, 1)))
        ret = div(price[i] - at(price, i, 1), at(price, i, 1))
        dmax.append(a1 * pmax(ret, 0) + (1 - a1) * nz(at(dmax, i, 1)))
        dmin.append(-a1 * pmin(ret, 0) + (1 - a1) * nz(at(dmin, i, 1)))
        bhb.append(beta * dmax[i])
        blb.append(beta * dmin[i])
        hb.append((1 + at(bhb, i, 1)) * ama[i])
        lb.append((1 - at(blb, i, 1)) * ama[i])
        r = div(price[i] - at(ama, i, 1), at(ama, i, 1))
        if price[i] > hb[i]:
            snr = div(r, blb[i])
        elif price[i] < lb[i]:
            snr = div(-r, bhb[i])
        else:
            snr = 0
        natan.append(NA if na(snr) else (math.atan(snrfactor * snr) + pi2) / (2 * pi2))
        w1 = wma_last(natan, lookback)  # minfactor + (max - min) * natan = natan
        av1.append(w1)
        w2 = wma_last(av1, int(fast))
        alpha.append((1 + al_n) * w1 - al_n * w2)
    r = xm.ama_durenard(C, lookback, beta, snrfactor)
    same(r.ama, ama, rtol=1e-8)
    same(r.upper, hb, rtol=1e-8)
    same(r.lower, lb, rtol=1e-8)


def test_ma_converging_luxalgo():
    length, incr, fast = 100, 10, 10
    upper, lower, init = p_highest(hi, length), p_lowest(lo, length), p_sma(cl, length)
    kk = 1 / incr
    ma_var, alpha_var = 0.0, 0.0
    ma_h, al_h, fma_h = [], [], []
    a_prev = b_prev = NA
    for i in range(N):
        src = cl[i]
        b = ma_var
        cross = p_cross(src, b, a_prev, b_prev)
        a_prev, b_prev = src, b
        if cross:
            alpha_var = 2 / (length + 1)
        elif src > b and upper[i] > at(upper, i, 1):
            alpha_var = alpha_var + kk
        elif src < b and lower[i] < at(lower, i, 1):
            alpha_var = alpha_var + kk
        m1, a1 = at(ma_h, i, 1), at(al_h, i, 1)
        ma_var = nz(m1 + a1 * (src - m1), init[i])
        f1 = at(fma_h, i, 1)
        if cross:
            e = (src + f1) / 2
        elif src > ma_var:
            e = pmax(src, f1) + (src - f1) / fast
        else:
            e = pmin(src, f1) + (src - f1) / fast
        ma_h.append(ma_var)
        al_h.append(alpha_var)
        fma_h.append(nz(e, src))
    r = xm.ma_converging(H, L, C, length, incr, fast)
    same(r.ma, ma_h, rtol=1e-8)
    same(r.fma, fma_h, rtol=1e-8)


# ---------------------------------------------------------------------------
# Durschner NMA, OBV MACD averages, Tillson GD
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("period", [5, 8, 20])
def test_nwma_cryptostatistical(period):
    fast = period / 2
    lam = period / fast
    alpha = lam * (period - 1) / (period - lam)
    a1 = p_wma(cl, period)
    a2 = p_wma(a1, int(fast))  # Pine truncates a float length
    same(xm.nma_durschner(C, period), [(1 + alpha) * x - alpha * y for x, y in zip(a1, a2)])


def _obv_ma(t, src, ln, len1=26):
    def ema(x, n):
        return p_ema(x, n)

    def dema(x, n):
        m1 = ema(x, n)
        return [2 * a - b for a, b in zip(m1, ema(m1, n))]

    def tema(x, n):
        m1 = ema(x, n)
        m2 = ema(m1, n)
        return [3 * (a - b) + d for a, b, d in zip(m1, m2, ema(m2, n))]

    def triple(f, x, n):
        m1 = f(x, n)
        m2 = f(m1, n)
        return [3 * (a - b) + d for a, b, d in zip(m1, m2, f(m2, n))]

    def zlsrc(x, n):
        lag = int(pround((n - 1) / 2))
        return [x[i] + (x[i] - at(x, i, lag)) for i in range(len(x))]

    def zlema(x, n):
        return ema(zlsrc(x, n), n)

    def nma(x, l1, l2):
        lam = l1 / l2
        al = lam * (l1 - 1) / (l1 - lam)
        m1 = ema(x, l1)
        return [(1 + al) * a - al * b for a, b in zip(m1, ema(m1, l2))]

    if t == "EMA":
        return ema(src, ln)
    if t == "DEMA":
        return dema(src, ln)
    if t == "TEMA":
        return tema(src, ln)
    if t == "TDEMA":
        return triple(dema, src, ln)
    if t == "TTEMA":
        return triple(tema, src, ln)
    if t == "THMA":
        return triple(_hma, src, ln)
    if t == "ZLEMA":
        return zlema(src, ln)
    if t == "ZLDEMA":
        return dema(zlsrc(src, ln), ln)
    if t == "ZLTEMA":
        return tema(zlsrc(src, ln), ln)
    if t == "DZLEMA":
        z1 = zlema(src, ln)
        return [2 * a - b for a, b in zip(z1, zlema(z1, ln))]
    if t == "TZLEMA":
        return triple(zlema, src, ln)
    if t == "LLEMA":
        return ema([0.25 * src[i] + 0.5 * at(src, i, 1) + 0.25 * at(src, i, 2) for i in range(len(src))], ln)
    if t == "NMA":
        return nma(src, ln, len1)
    return [(a + b) / 2 for a, b in zip(triple(tema, src, ln), triple(dema, src, ln))]


@pytest.mark.parametrize("t", xm._OBV_TYPES)
@pytest.mark.parametrize("ln", [9, 10])
def test_obv_macd_ma(t, ln):
    same(xm.obv_macd_ma(C, ln, t), _obv_ma(t, cl, ln), rtol=1e-8, atol=1e-8)


def test_tillson_gd():
    n, f = 5, 0.7
    e = p_ema(cl, n)
    same(xm.tillson_gd(C, n, f), [a * (1 + f) - b * f for a, b in zip(e, p_ema(e, n))])


# ---------------------------------------------------------------------------
# Step / deadband lines
# ---------------------------------------------------------------------------

def test_step_line_tstep_form():
    band = [0.3 + 0.2 * math.sin(i / 7) for i in range(N)]
    band[50:55] = [NA] * 5
    out, b = [], NA
    for i in range(N):
        src, a = cl[i], band[i]
        b = src if src > nz(b, src) + a else src if src < nz(b, src) - a else nz(b, src)
        out.append(b)
    same(xm.step_line(C, pd.Series(band, index=C.index)), out)


def test_tchannels_obv_macd_b5():
    src15 = lin(xm.obv_macd_ma(C, 9, "DEMA").to_numpy())  # any series with a warm-up
    p = 1
    b5, dev5, oc, out_b, out_d, out_o = NA, NA, NA, [], [], []
    cum, seen = 0.0, False
    for i in range(N):
        n5 = i  # cum(1) - 1
        e = abs(src15[i] - nz(b5, src15[i]))
        if not na(e):
            cum += e
            seen = True
        a15 = div(cum, n5) * p if seen else NA
        prev = b5
        src = src15[i]
        b5 = src if src > nz(b5, src) + a15 else src if src < nz(b5, src) - a15 else nz(b5, src)
        ch = b5 - prev
        dev5 = a15 if (not na(ch) and ch != 0) else nz(dev5, a15)
        oc = 1 if ch > 0 else -1 if ch < 0 else nz(oc)
        out_b.append(b5)
        out_d.append(dev5)
        out_o.append(oc)
    r = xm.tchannels(pd.Series(src15, index=C.index), 1.0)
    same(r.line, out_b)
    same(r.band, out_d)
    same(r.trend, out_o)


def test_tstep_lsma_alexgrover():
    length, sc = 100, 0.5
    src, bb, ls_l = [], [], []
    b = NA
    cum = 0.0
    alpha_f = NA
    osc, osc_l = NA, []
    for i in range(N):
        src.append(sc * cl[i] + (1 - sc) * nz(at(ls_l, i, 1), cl[i]))
        if i >= length:
            den = sum(abs(src[i - j] - src[i - j - 1]) for j in range(length))
            er = 1 - div(abs(src[i] - src[i - length]), den)
        else:
            er = NA
        n = i
        cum += abs(src[i] - nz(b, src[i]))
        a = div(cum, n) * (1 + er)
        prev = b
        s = src[i]
        b = s if s > nz(b, s) + a else s if s < nz(b, s) - a else nz(b, s)
        bb.append(b)
        osc = 1 if b > prev else 0 if b < prev else osc
        osc_l.append(osc)
        ls = NA
        if i >= length - 1:
            xs, ys = src[i - length + 1:i + 1], bb[i - length + 1:i + 1]
            mx, my = sum(xs) / length, sum(ys) / length

            def dev(t, m):  # Pine stdev's SUM(): |x - avg| <= 1e-10 is 0
                d_ = t - m
                return 0.0 if abs(d_) <= 1e-10 else d_
            sxy = sum(dev(p, mx) * dev(q, my) for p, q in zip(xs, ys))
            sxx = sum(dev(p, mx) ** 2 for p in xs)
            syy = sum(dev(q, my) ** 2 for q in ys)
            if sxx > 0 and syy > 0:  # correlation * stdev(src)/stdev(b), fixnan
                alpha_f = sxy / math.sqrt(sxx * syy) * (math.sqrt(sxx / length) / math.sqrt(syy / length))
            ls = alpha_f * b + (mx - alpha_f * my)
        ls_l.append(ls)
    r = xm.tstep_lsma(C, length, sc)
    same(r.step, bb, rtol=1e-8)
    same(r.tstep, ls_l, rtol=1e-8)
    same(r.trend, osc_l)


def test_deadband_double_sma_goblin_town():
    length_, gamma = 15, 4.0
    src_ = cl
    dsrc = op  # the script's `src` input is open
    mad, xs, inner = [], [], []
    cum, seen = 0.0, False
    for i in range(N):
        ma = nz(at(mad, i, 1), src_[i])
        e = abs(at(dsrc, i, length_) - ma)
        if not na(e):
            cum += e
            seen = True
        d = div(cum, i) * gamma if seen else NA
        base = nz(at(mad, i, 1), src_[i])
        xs.append(src_[i] + d if src_[i] > base + d else src_[i] - d if src_[i] < base - d else base)
        inner.append(sma_last(xs, length_))
        mad.append(sma_last(inner, length_))
    same(xm.deadband_double_sma(C, O, length_, gamma), mad, rtol=1e-8)


def test_lazy_line():
    x = lin(xm.obv_macd_ma(C, 20, "EMA").to_numpy())
    lzf = 0.04 / 10
    out, lz = [], NA
    for i in range(N):
        s = NA if na(x[i]) else float(np.sign(x[i]))
        if x[i] == nz(at(x, i, 1), x[i]):
            lz = x[i]
        elif x[i] > nz(lz + lzf * lz * s, x[i]):
            lz = x[i]
        elif x[i] < nz(lz - lzf * lz * s, x[i]):
            lz = x[i]
        out.append(lz)
    same(xm.hysteresis_filter(pd.Series(x, index=C.index), lzf), out)


@pytest.mark.parametrize("recursive", [False, True])
def test_ratio_ochl_averager(recursive):
    H_ = [at(hi, i, 1) for i in range(N)]
    L_ = [at(lo, i, 1) for i in range(N)]
    out, d = [], NA
    for i in range(N):
        a = nz(d, op[i]) if recursive else op[i]
        b = div(abs(cl[i] - a), H_[i] - L_[i])
        cc = 1 if b > 1 else b
        d = cc * cl[i] + (1 - cc) * nz(d, cl[i])
        out.append(d)
    same(xm.ratio_ochl_averager(O, C, H.shift(1), L.shift(1), recursive), out)


# ---------------------------------------------------------------------------
# Other recursions
# ---------------------------------------------------------------------------

def test_rema_satchwell():
    p, lam = 10, 0.5
    a = 2 / (p + 1)
    out = []
    for i in range(N):
        r1, r2 = at(out, i, 1), at(out, i, 2)
        out.append((nz(r1) + a * (cl[i] - nz(r1)) + lam * (2 * nz(r1) - nz(r2))) / (lam + 1))
    same(xm.rema(C, p, lam), out)
    pr = xm.rema(C, p, lam, seed="price").to_numpy()
    same(pr[-1000:], out[-1000:], rtol=1e-6)  # the seed only matters during warm-up


def test_ahrens_ma():
    n = 9
    out = []
    for i in range(N):
        a1, an = at(out, i, 1), at(out, i, n)
        out.append(nz(a1) + (cl[i] - (nz(a1) + nz(an)) / 2) / n)
    same(xm.ahrens_ma(C, n), out)
    same(xm.ahrens_ma(C, n, seed="price").to_numpy()[-1000:], out[-1000:], rtol=1e-6)


def test_essma_bhavishya():
    n, w = 50, (2.0, 3.0, 1.5, 2.5, 4.0)
    w1, w2, w3, w4, w5 = w
    x4 = [t * w4 for t in cl]
    s4 = p_sma(x4, n)
    smma = []
    for i in range(N):
        p2 = at(smma, i, 2)
        smma.append(s4[i] if na(p2) else (p2 * (n - 1) + x4[i]) / n)
    ema = p_ema([t * w2 for t in cl], n)
    sma = p_sma([t * w1 for t in cl], n)
    wma = p_wma([t * w3 for t in cl], n)
    rma = p_rma([t * w5 for t in cl], n)
    out = [(smma[i] / w4 + ema[i] / w2 + sma[i] / w1 - wma[i] / w3 - rma[i] / w5 + op[i] + cl[i]) / 3
           for i in range(N)]
    same(xm.essma(C, O, C, n, w1, w2, w3, w4, w5), out, rtol=1e-8)


def test_conditional_ema():
    n = 10
    cond = [cl[i] > op[i] for i in range(N)]
    x = [NA if i in (3, 4, 400) else cl[i] for i in range(N)]
    val, ema_val, out = [], [NA], []
    for i in range(N):
        if cond[i]:
            val.append(x[i])
            if len(val) > 1:
                val.pop(0)
            if na(ema_val[0]):
                ema_val = [val[0]]
            ema_val[0] = (val[0] - ema_val[0]) * (2 / (n + 1)) + ema_val[0]
        out.append(ema_val[0])
    same(xm.conditional_ema(pd.Series(x, index=C.index), pd.Series(np.array(cond, float), index=C.index), n),
         out)


def test_knn_mean_zeiierman():
    kn, ws = 3, 30
    value = cl
    target = p_sma(cl, 5)
    out = []
    for i in range(N):
        dists = [1e10] * kn
        vals = [0.0] * kn
        for j in range(1, ws + 1):
            val = at(value, i, j)
            dist = abs(target[i] - val)
            mi, mv = 0, dists[0]
            for q in range(1, kn):
                if dists[q] > mv:
                    mi, mv = q, dists[q]
            if dist < mv:
                dists[mi] = dist
                vals[mi] = val
        out.append(NA if 1e10 in dists else sum(vals) / kn)
    same(xm.knn_mean(C, pd.Series(target, index=C.index), kn, ws), out)


def test_jurik_rsx_copy():
    length = 14
    f90_ = f88 = f8 = []
    f90_l, f88_l, f8_l = [], [], []
    st = {k_: [] for k_ in ("f28", "f30", "f38", "f40", "f48", "f50", "f58", "f60", "f68", "f70", "f78", "f80")}
    out = []

    def p(name, i):
        return nz(at(st[name], i, 1))

    for i in range(N):
        src = cl[i]
        f90_ = 1.0 if nz(at(f90_l, i, 1)) == 0.0 else (nz(at(f88_l, i, 1)) + 1 if nz(at(f88_l, i, 1)) <= nz(at(f90_l, i, 1)) else nz(at(f90_l, i, 1)) + 1)
        f88 = length - 1.0 if (nz(at(f90_l, i, 1)) == 0.0) and (length - 1 >= 5) else 5.0
        f8 = 100.0 * src
        f18 = 3.0 / (length + 2.0)
        f20 = 1.0 - f18
        f10 = nz(at(f8_l, i, 1))
        v8 = f8 - f10
        f28 = f20 * p("f28", i) + f18 * v8
        f30 = f18 * f28 + f20 * p("f30", i)
        vC = f28 * 1.5 - f30 * 0.5
        f38 = f20 * p("f38", i) + f18 * vC
        f40 = f18 * f38 + f20 * p("f40", i)
        v10 = f38 * 1.5 - f40 * 0.5
        f48 = f20 * p("f48", i) + f18 * v10
        f50 = f18 * f48 + f20 * p("f50", i)
        v14 = f48 * 1.5 - f50 * 0.5
        f58 = f20 * p("f58", i) + f18 * abs(v8)
        f60 = f18 * f58 + f20 * p("f60", i)
        v18 = f58 * 1.5 - f60 * 0.5
        f68 = f20 * p("f68", i) + f18 * v18
        f70 = f18 * f68 + f20 * p("f70", i)
        v1C = f68 * 1.5 - f70 * 0.5
        f78 = f20 * p("f78", i) + f18 * v1C
        f80 = f18 * f78 + f20 * p("f80", i)
        v20 = f78 * 1.5 - f80 * 0.5
        f0 = 1.0 if ((f88 >= f90_) and (f8 != f10)) else 0.0
        f90 = 0.0 if ((f88 == f90_) and (f0 == 0.0)) else f90_
        v4_ = (v14 / v20 + 1.0) * 50.0 if ((f88 < f90) and (v20 > 0.0000000001)) else 50.0
        rsx = (100.0 if v4_ > 100.0 else 0.0 if v4_ < 0.0 else v4_) - 50
        out.append(rsx)
        f90_l.append(f90_)
        f88_l.append(f88)
        f8_l.append(f8)
        for name, val in (("f28", f28), ("f30", f30), ("f38", f38), ("f40", f40), ("f48", f48), ("f50", f50),
                          ("f58", f58), ("f60", f60), ("f68", f68), ("f70", f70), ("f78", f78), ("f80", f80)):
            st[name].append(val)
    same(xm.jurik_rsx(C, length) - 50, out, rtol=1e-8, atol=1e-8)


# ---------------------------------------------------------------------------
# FTSMA, MoonFlag, RWMA
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("k_", [1, 3])
def test_ftsma_03freeman(k_):
    def f_pi(n_):
        a = 1. / (4. * n_ + 2)
        b = 1. / (6. * n_ + 3)
        for i_ in range(n_ - 1, -1, -1):
            a = 1 / (4. * i_ + 2) - a / 4.
            b = 1 / (6. * i_ + 3) - b / 9.
        return (4. * a) + (4. * b) - 0.

    pi = f_pi(20)
    nn, ma_len = 64, 20
    sig = []
    for i in range(N):
        s = 0.0
        for j in range(nn):
            s += at(cl, i, j) * math.cos(2 * pi * k_ * j / nn)
        rex_ = 2 * s / nn if (k_ != 0 and k_ != nn / 2) else s / nn
        sig.append(cl[i] + (rex_ * math.cos(0) + (-2 * 0.0 / nn) * math.sin(0)))
    same(xm.ftsma(C, k_, ma_len, nn, "ema"), p_ema(sig, ma_len), rtol=1e-8)


def test_moonflag_average():
    def d(g, data):
        a = p_wma(data, int(pround((g - pround(g / 3)) / 2)))
        b = p_wma(a, int(pround(g / 3)))
        return p_wma(b, int((g - pround(g / 3)) / 2))

    for g in (12, 26, 9):
        same(xm.moonflag_average(C, g), d(g, d(g, d(g, cl))))


def test_rwma_tzack88():
    n = 20
    rng = [a - b for a, b in zip(hi, lo)]
    srng = p_sum(rng, n)
    w = [div(a, b) for a, b in zip(rng, srng)]
    num = p_sum([a * b for a, b in zip(cl, w)], n)
    den = p_sum(w, n)
    same(xm.rwma_range(H, L, C, n), [div(a, b) for a, b in zip(num, den)], rtol=1e-8)


# ---------------------------------------------------------------------------
# Plumbing
# ---------------------------------------------------------------------------

def test_registry_and_dataframe_shapes():
    import tv_indicators._core as core
    assert xm.EXTRA_MA and not set(xm.EXTRA_MA) & set(core.REGISTRY)
    df = pd.DataFrame({"a": C, "b": C * 1.1})
    r = xm.henderson_ma(df, 7)
    assert isinstance(r, pd.DataFrame) and r.shape == df.shape
    same(r["b"], xm.henderson_ma(C * 1.1, 7))
    u = xm.uhl_ma(df, 50)
    same(u.cts["a"], xm.uhl_ma(C, 50).cts)
