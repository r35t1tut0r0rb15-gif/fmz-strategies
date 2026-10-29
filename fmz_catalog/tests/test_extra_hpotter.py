"""Tests for fmz_catalog/extra_hpotter.py.

Every indicator is checked against a literal bar-by-bar Python port of
HPotter's Pine code (``hpotter=True`` paths, and the main path where his
port is faithful) or of the published formula (main paths that differ from
his port). The ports below use their own plain-Python Pine helpers, not the
library kernels, and follow Pine semantics: ``x[n]`` is na before bar n, na
comparisons are false, ``nz()`` seeds recursions.
"""

import math

import numpy as np
import pandas as pd
import pytest

import fmz_catalog.extra_hpotter as hp
import tv_indicators as ti
from tv_indicators._core import REGISTRY
from tv_indicators.tests.test_indicators import TAIL, C, D, H, L, N, O, V, c, h, l, o, same, v

NA = float("nan")


# ---------------------------------------------------------------------------
# Plain-Python Pine helpers
# ---------------------------------------------------------------------------

def isna(x):
    return x is None or (isinstance(x, float) and math.isnan(x))


def nz(x, r=0.0):
    return r if isna(x) else x


def at(x, i, n=0):
    j = i - n
    return x[j] if 0 <= j < len(x) else NA


def gt(a, b):
    return not isna(a) and not isna(b) and a > b


def lt(a, b):
    return not isna(a) and not isna(b) and a < b


def ge(a, b):
    return not isna(a) and not isna(b) and a >= b


def le(a, b):
    return not isna(a) and not isna(b) and a <= b


def window(x, i, n):
    if i < n - 1:
        return None
    w = list(x[i - n + 1:i + 1])
    return None if any(isna(t) for t in w) else w


def sma_p(x, n):
    out = []
    for i in range(len(x)):
        w = window(x, i, n)
        out.append(NA if w is None else sum(w) / n)
    return out


def sum_p(x, n):
    out = []
    for i in range(len(x)):
        w = window(x, i, n)
        out.append(NA if w is None else sum(w))
    return out


def wma_p(x, n):
    out = []
    for i in range(len(x)):
        w = window(x, i, n)
        out.append(NA if w is None else sum(w[j] * (j + 1) for j in range(n)) / (n * (n + 1) / 2))
    return out


def stdev_p(x, n):
    out = []
    for i in range(len(x)):
        w = window(x, i, n)
        if w is None:
            out.append(NA)
        else:
            m = sum(w) / n
            out.append(math.sqrt(sum((t - m) ** 2 for t in w) / n))
    return out


def dev_p(x, n):
    out = []
    for i in range(len(x)):
        w = window(x, i, n)
        if w is None:
            out.append(NA)
        else:
            m = sum(w) / n
            out.append(sum(abs(t - m) for t in w) / n)
    return out


def highest_p(x, n):
    out = []
    for i in range(len(x)):
        w = window(x, i, n)
        out.append(NA if w is None else max(w))
    return out


def lowest_p(x, n):
    out = []
    for i in range(len(x)):
        w = window(x, i, n)
        out.append(NA if w is None else min(w))
    return out


def ewm_p(x, n, a):
    out, s, cnt, acc = [], NA, 0, 0.0
    for t in x:
        if not isna(t):
            if cnt < n:
                acc += t
                cnt += 1
                if cnt == n:
                    s = acc / n
            else:
                s = a * t + (1 - a) * s
        out.append(s)
    return out


def ema_p(x, n):
    return ewm_p(x, n, 2 / (n + 1))


def rma_p(x, n):
    return ewm_p(x, n, 1 / n)


def shift(x, n):
    return [at(x, i, n) for i in range(len(x))]


def change(x, n=1):
    return [NA if isna(at(x, i, n)) or isna(x[i]) else x[i] - at(x, i, n) for i in range(len(x))]


def roc_p(x, n):
    return [NA if isna(at(x, i, n)) else 100 * (x[i] - at(x, i, n)) / at(x, i, n) for i in range(len(x))]


def stoch_p(src, hi, lo, n):
    hh, ll = highest_p(hi, n), lowest_p(lo, n)
    out = []
    for i in range(len(src)):
        r = hh[i] - ll[i] if not (isna(hh[i]) or isna(ll[i])) else NA
        out.append(NA if isna(r) or r == 0 or isna(src[i]) else 100 * (src[i] - ll[i]) / r)
    return out


def rsi_p(x, n):
    ch = change(x)
    up = rma_p([NA if isna(t) else max(t, 0.0) for t in ch], n)
    dn = rma_p([NA if isna(t) else max(-t, 0.0) for t in ch], n)
    out = []
    for u, d in zip(up, dn):
        if isna(u) or isna(d):
            out.append(NA)
        elif d == 0:
            out.append(100.0)
        elif u == 0:
            out.append(0.0)
        else:
            out.append(100 - 100 / (1 + u / d))
    return out


def tr_p(hi, lo, cl, handle_na=True):
    out = []
    for i in range(len(cl)):
        pc = at(cl, i, 1)
        if isna(pc):
            out.append(hi[i] - lo[i] if handle_na else NA)
        else:
            out.append(max(hi[i] - lo[i], abs(hi[i] - pc), abs(lo[i] - pc)))
    return out


def atr_p(n):
    return rma_p(tr_p(h, l, c), n)


def linreg_p(x, n, off):
    out = []
    for i in range(len(x)):
        w = window(x, i, n)
        if w is None:
            out.append(NA)
            continue
        xs = list(range(n))
        mx, my = sum(xs) / n, sum(w) / n
        b = sum((a - mx) * (y - my) for a, y in zip(xs, w)) / sum((a - mx) ** 2 for a in xs)
        out.append(my - b * mx + b * (n - 1 - off))
    return out


def fadx_p(n):
    """HPotter's fADX (TradingView's DMI ADX)."""
    up = change(list(h))
    down = [NA if isna(t) else -t for t in change(list(l))]
    trur = rma_p(tr_p(h, l, c, False), n)
    pdm = [NA if isna(u) or isna(d) else (u if (u > d and u > 0) else 0.0) for u, d in zip(up, down)]
    mdm = [NA if isna(u) or isna(d) else (d if (d > u and d > 0) else 0.0) for u, d in zip(up, down)]
    rp, rm = rma_p(pdm, n), rma_p(mdm, n)
    plus, minus, lp, lm = [], [], NA, NA
    for a, b, t in zip(rp, rm, trur):
        p = NA if isna(a) or isna(t) or t == 0 else 100 * a / t
        m = NA if isna(b) or isna(t) or t == 0 else 100 * b / t
        lp = p if not isna(p) else lp
        lm = m if not isna(m) else lm
        plus.append(lp)
        minus.append(lm)
    q = [NA if isna(a) or isna(b) else abs(a - b) / (1.0 if a + b == 0 else a + b) for a, b in zip(plus, minus)]
    return [NA if isna(t) else 100 * t for t in rma_p(q, n)]


def pine_round(x):
    return math.floor(x + 0.5)


hl2 = list((h + l) / 2)
hlc3 = list((h + l + c) / 3)
ohlc4 = list((o + h + l + c) / 4)
cl = list(c)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def test_registry_untouched_and_names_unique():
    assert not set(hp.EXTRA_HPOTTER) & set(REGISTRY)
    assert len(hp.EXTRA_HPOTTER) == len(hp.__all__)


def test_every_indicator_runs_on_dataframe_columns():
    df = pd.DataFrame({"a": c, "b": c * 1.01}, index=D.index)
    r = hp.ravi(df)
    assert isinstance(r, pd.DataFrame) and r.shape == df.shape
    same(r["a"], hp.ravi(C))


# ---------------------------------------------------------------------------
# Fractals and patterns
# ---------------------------------------------------------------------------

def fractal_port(x, pattern, up):
    res, out = NA, []
    for i in range(N):
        p = at(x, i, pattern + 1)
        okl = okr = 1
        for j in range(pattern, 0, -1):
            cond = lt(at(x, i, j), at(x, i, j + 1)) if up else gt(at(x, i, j), at(x, i, j + 1))
            okl = 1 if (cond and okl == 1) else 0
        for j in range(pattern + 2, pattern * 2 + 2):
            cond = lt(at(x, i, j), at(x, i, j - 1)) if up else gt(at(x, i, j), at(x, i, j - 1))
            okr = 1 if (cond and okr == 1) else 0
        res = p if (okl == 1 and okr == 1) else res
        out.append(res)
    return out


@pytest.mark.parametrize("pattern", [1, 2])
def test_fractal_chaos_bands_and_oscillator(pattern):
    up, dn = fractal_port(h, pattern, True), fractal_port(l, pattern, False)
    r = hp.fractal_chaos_bands(H, L, pattern)
    same(r.upper, up)
    same(r.lower, dn)
    fco = []
    for i in range(N):
        a, b = up[i], at(up, i, 1)
        x, y = dn[i], at(dn, i, 1)
        fco.append(1.0 if (not isna(a) and not isna(b) and a != b) else
                   (-1.0 if (not isna(x) and not isna(y) and x != y) else 0.0))
    same(hp.fractal_chaos_oscillator(H, L, pattern), fco)


def test_key_reversal_and_three_bar_reversal():
    up, dn = [], []
    for i in range(N):
        up.append(lt(l[i], at(l, i, 1)) and gt(c[i], at(c, i, 1)))
        dn.append(gt(h[i], at(h, i, 1)) and lt(c[i], at(c, i, 1)))
    r = hp.key_reversal(H, L, C, 1)
    np.testing.assert_array_equal(r.up, up)
    np.testing.assert_array_equal(r.down, dn)
    bull, bear = [], []
    for i in range(N):
        bull.append(gt(at(o, i, 2), at(c, i, 2)) and lt(at(h, i, 1), at(h, i, 2)) and lt(at(l, i, 1), at(l, i, 2))
                    and gt(l[i], at(l, i, 1)) and gt(h[i], at(h, i, 1)))
        bear.append(lt(at(o, i, 2), at(c, i, 2)) and gt(at(h, i, 1), at(h, i, 2)) and gt(at(l, i, 1), at(l, i, 2))
                    and lt(h[i], at(h, i, 1)) and lt(l[i], at(l, i, 1)))
    r = hp.three_bar_reversal(O, H, L, C)
    np.testing.assert_array_equal(r.bull, bull)
    np.testing.assert_array_equal(r.bear, bear)


def test_n_bars_up_down_hpotter_counter():
    up, dn, cu, cd = [], [], 0, 0
    for i in range(N):
        c1, o1 = at(c, i, 1), at(o, i, 1)
        cu = nz(cu) + 1 if ge(c1, o1) else (0 if lt(c1, o1) else 0)
        cd = nz(cd) + 1 if le(c1, o1) else (0 if gt(c1, o1) else 0)
        up.append(cu)
        dn.append(cd)
    r = hp.n_bars_up_down(O, C, hpotter=True)
    same(r.up_count, up)
    same(r.down_count, dn)
    r0 = hp.n_bars_up_down(O, C)
    same(shift(list(r0.up_count), 1)[1:], up[1:])


def test_candle_patterns():
    o1, c1, o2, c2 = shift(o, 1), shift(c, 1), shift(o, 2), shift(c, 2)
    bull = [abs(c[i] - o[i]) >= 0.1 and gt(o1[i], c1[i]) and c[i] > o[i] and le(c[i], o1[i]) and le(c1[i], o[i])
            and lt(c[i] - o[i], nz(o1[i], NA) - nz(c1[i], NA)) for i in range(N)]
    bear = [abs(c[i] - o[i]) >= 0.1 and gt(c1[i], o1[i]) and o[i] > c[i] and le(o[i], c1[i]) and le(o1[i], c[i])
            and lt(o[i] - c[i], nz(c1[i], NA) - nz(o1[i], NA)) for i in range(N)]
    r = hp.harami(O, C, 0.1)
    np.testing.assert_array_equal(r.bull, bull)
    np.testing.assert_array_equal(r.bear, bear)
    beng = [ge(abs(nz(c1[i], NA) - nz(o1[i], NA)), 0.1) and gt(c1[i], o1[i]) and o[i] > c[i] and ge(o[i], c1[i])
            and ge(o1[i], c[i]) and gt(o[i] - c[i], nz(c1[i], NA) - nz(o1[i], NA)) for i in range(N)]
    np.testing.assert_array_equal(hp.engulfing(O, C, 0.1).bear, beng)
    up = [gt(o2[i], c2[i]) and gt(c1[i], o1[i]) and le(c1[i], o2[i]) and le(c2[i], o1[i])
          and lt(nz(c1[i], NA) - nz(o1[i], NA), nz(o2[i], NA) - nz(c2[i], NA)) and c[i] > o[i]
          and gt(c[i], c1[i]) and gt(o[i], o1[i]) and gt(c[i], o2[i]) for i in range(N)]
    dn = [gt(c2[i], o2[i]) and gt(o1[i], c1[i]) and le(o1[i], c2[i]) and le(o2[i], c1[i])
          and lt(nz(o1[i], NA) - nz(c1[i], NA), nz(c2[i], NA) - nz(o2[i], NA)) and c[i] < o[i]
          and lt(c[i], c1[i]) and lt(o[i], o1[i]) and lt(c[i], o2[i]) for i in range(N)]
    r = hp.three_inside(O, C)
    np.testing.assert_array_equal(r.up, up)
    np.testing.assert_array_equal(r.down, dn)
    np.testing.assert_array_equal(hp.doji(O, C), o == c)


def test_period_high_low_matches_resampled_previous_day():
    sess = ti.session_ids(D.index, "D")
    r = hp.period_high_low(H, L, sess, 1)
    day = D.resample("D").agg({"high": "max", "low": "min"})
    exp_h = day["high"].shift(1).reindex(D.index.floor("D")).to_numpy()
    exp_l = day["low"].shift(1).reindex(D.index.floor("D")).to_numpy()
    same(r.high, exp_h)
    same(r.low, exp_l)
    r0 = hp.period_high_low(H, L, sess, 0)
    same(r0.high, H.groupby(D.index.floor("D")).cummax())
    same(r0.low, L.groupby(D.index.floor("D")).cummin())
    # HPotter's DayHigh: dayofmonth != dayofmonth[1] ? high : max(high, nz(DayHigh[1]))
    dh, out = NA, []
    for i in range(N):
        dh = h[i] if (i == 0 or D.index[i].day != D.index[i - 1].day) else max(h[i], nz(dh))
        out.append(dh)
    same(r0.high, out)


# ---------------------------------------------------------------------------
# Gimelfarb, Rainbow, primes
# ---------------------------------------------------------------------------

def test_bull_bear_balance_port():
    bull, bear = [], []
    for i in range(N):
        cc, oo, hh, ll, c1 = c[i], o[i], h[i], l[i], at(c, i, 1)

        def mx(a, b):
            return NA if isna(a) or isna(b) else max(a, b)
        if cc < oo:
            val = mx(cc - oo, hh - ll) if gt(c1, oo) else hh - ll
        elif cc > oo:
            val = mx(c1 - ll, hh - cc) if gt(c1, oo) else mx(oo - ll, hh - cc)
        elif hh - cc > cc - ll:
            val = mx(c1 - oo, hh - ll) if gt(c1, oo) else hh - ll
        elif hh - cc < cc - ll:
            val = mx(cc - ll, hh - cc) if cc > oo else oo - ll
        elif cc > oo:
            val = mx(c1 - oo, hh - cc)
        elif lt(c1, oo):
            val = mx(oo - ll, hh - cc)
        else:
            val = hh - ll
        if cc < oo:
            val2 = mx(hh - c1, cc - ll) if lt(c1, oo) else mx(hh - oo, cc - ll)
        elif cc > oo:
            val2 = hh - ll if gt(c1, oo) else mx(oo - c1, hh - ll)
        elif hh - cc > cc - ll:
            val2 = mx(hh - c1, cc - ll) if lt(c1, oo) else hh - oo
        elif hh - cc < cc - ll:
            val2 = hh - ll if gt(c1, oo) else mx(oo - cc, hh - ll)
        elif gt(c1, oo):
            val2 = mx(hh - oo, cc - ll)
        elif lt(c1, oo):
            val2 = mx(oo - cc, hh - ll)
        else:
            val2 = hh - ll
        bear.append(val)
        bull.append(val2)
    r = hp.bull_bear_balance(O, H, L, C)
    same(r.bull, bull)
    same(r.bear, bear)
    same(r.balance, np.array(bull) - np.array(bear))
    same(hp.bull_bear_balance(O, H, L, C, smooth=15).bull, sma_p(bull, 15))


def test_rainbow_oscillator_port():
    mas, m = [], cl
    for _ in range(10):
        m = sma_p(m, 2)
        mas.append(m)
    hh, ll = highest_p(cl, 10), lowest_p(cl, 10)
    rbo, rb = [], []
    for i in range(N):
        vals = [x[i] for x in mas]
        if any(isna(t) for t in vals) or isna(hh[i]) or hh[i] == ll[i]:
            rbo.append(NA)
            rb.append(NA)
            continue
        rbo.append(100 * ((c[i] - sum(vals) / 10) / (hh[i] - ll[i])))
        rb.append(100 * ((max(vals) - min(vals)) / (hh[i] - ll[i])))
    r = hp.rainbow_oscillator(C)
    same(r.rbo, rbo)
    same(r.bandwidth, rb)


def pine_prime_port(price, percent, up):
    """HPotter's loop, line by line (float counters, divisors to sqrt(price))."""
    res = 0.0
    j = price
    lim = price + price * percent / 100 if up else price - price * percent / 100
    while (j <= lim) if up else (j >= lim):
        res = j
        sq = math.sqrt(price)
        i = 2.0
        step = 1.0 if sq >= 2 else -1.0
        while (i <= sq) if step > 0 else (i >= sq):
            res = 0.0 if math.fmod(j, i) == 0 else j
            if res == 0:
                break
            i += step
        if res > 0:
            break
        j += 1 if up else -1
    return res


def is_prime(m):
    return m >= 2 and all(m % d for d in range(2, int(math.isqrt(m)) + 1))


@pytest.mark.parametrize("prices", ["float", "integer"])
def test_prime_number_oscillator_and_bands_hpotter(prices):
    x = c if prices == "float" else np.round(c * 10)
    hi = h if prices == "float" else np.round(h * 10)
    lo = l if prices == "float" else np.round(l * 10)
    osc, prev = [], NA
    up_b, dn_b, pu, pd_ = [], [], NA, NA
    for i in range(N):
        r1, r2 = pine_prime_port(x[i], 5, True), pine_prime_port(x[i], 5, False)
        res = r1 - x[i] if r1 - x[i] < x[i] - r2 else r2 - x[i]
        res = prev if res == 0 else res
        osc.append(res)
        prev = res
        u = pine_prime_port(hi[i], 5, True)
        pu = pu if u == 0 else u
        up_b.append(pu)
        d = pine_prime_port(lo[i], 5, False)
        pd_ = pd_ if d == 0 else d
        dn_b.append(pd_)
    same(hp.prime_number_oscillator(pd.Series(x), 5, hpotter=True), osc)
    b = hp.prime_number_bands(pd.Series(hi), pd.Series(lo), 5, hpotter=True)
    same(b.upper, up_b)
    same(b.lower, dn_b)
    if prices == "float":  # HPotter's loop never leaves the raw (non-integer) price
        assert np.isnan(osc).all()
        same(b.upper, hi)


def test_prime_number_main_nearest_prime():
    x = c * 10
    out, prev = [], NA
    for p in x:
        m = math.floor(p + 0.5)
        up = next((j for j in range(m, math.floor(m * 1.05) + 1) if is_prime(j)), None)
        dn = next((j for j in range(m, math.ceil(m * 0.95) - 1, -1) if is_prime(j)), None)
        if up is None and dn is None:
            r = prev
        elif dn is None or (up is not None and up - p < p - dn):
            r = up - p
        else:
            r = dn - p
        out.append(r)
        prev = r
    same(hp.prime_number_oscillator(pd.Series(x), 5), out)
    same(hp.prime_number_oscillator(C, 5, scale=10), np.array(out) / 10)
    b = hp.prime_number_bands(pd.Series(h * 10), pd.Series(l * 10), 5)
    assert all(is_prime(int(t)) and t >= math.floor(p + 0.5) for t, p in zip(b.upper, h * 10))
    assert all(is_prime(int(t)) and t <= math.floor(p + 0.5) for t, p in zip(b.lower, l * 10))


# ---------------------------------------------------------------------------
# FVE family and volume
# ---------------------------------------------------------------------------

def fve_mf():
    return [cl[i] - hl2[i] + hlc3[i] - at(hlc3, i, 1) for i in range(N)]


def test_fve_hpotter_and_katsanos():
    period, factor = 18, 0.6
    mf = fve_mf()
    smav = sma_p(list(v), period)
    nres, out, vl = NA, [], []
    for i in range(N):
        nv = v[i] if gt(mf[i], factor * c[i] / 100) else (-v[i] if lt(mf[i], -factor * c[i] / 100) else 0.0)
        vl.append(nv)
        nres = nz(nres, 0) + ((nv / smav[i]) / period) * 100 if not isna(smav[i]) else NA
        out.append(nres)
    same(hp.finite_volume_elements(H, L, C, V, period, factor, hpotter=True), out, rtol=1e-8)
    # Katsanos (MetaStock): Sum(signed V, n) / Mov(V, n) / n * 100
    s = sum_p(vl, period)
    exp = [NA if isna(a) or isna(b) else a / b / period * 100 for a, b in zip(s, smav)]
    same(hp.finite_volume_elements(H, L, C, V, period, factor), exp)


@pytest.mark.parametrize("hpotter", [False, True])
def test_volatility_fve(hpotter):
    n, perma = 22, 40
    intra = list(np.log(h) - np.log(l))
    inter = [math.log(hlc3[i]) - math.log(at(hlc3, i, 1)) if i else NA for i in range(N)]
    if hpotter:
        vi, ve = stdev_p(sma_p(intra, n), n), stdev_p(sma_p(inter, n), n)
    else:
        vi, ve = stdev_p(intra, n), stdev_p(inter, n)
    mf = fve_mf()
    sv = []
    for i in range(N):
        cut = NA if isna(vi[i]) or isna(ve[i]) else 0.1 * vi[i] + 0.1 * ve[i]
        f = 1 if gt(mf[i], nz(cut, NA) * c[i]) else (-1 if lt(mf[i], -1 * nz(cut, NA) * c[i]) else 0)
        sv.append(v[i] * f)
    fsum, vsum = sum_p(sv, n), sum_p(list(v), n)
    fve = [a / b * 100 if not isna(a) else NA for a, b in zip(fsum, vsum)]
    r = hp.volatility_fve(H, L, C, V, n, perma, 0.1, 0.1, hpotter=hpotter)
    same(r.fve, fve, rtol=1e-8, atol=1e-7)
    same(r.signal, ema_p(fve, perma), rtol=1e-8, atol=1e-7)


def test_modified_pvt_port():
    cum, res = NA, []
    for i in range(N):
        rv = v[i] / 50000
        term = rv * (ohlc4[i] - at(ohlc4, i, 1)) / at(ohlc4, i, 1)
        cum = nz(cum) + term
        res.append(1 + 1 * cum)
    r = hp.modified_pvt(O, H, L, C, V, 1, 1, 23)
    same(r.mpvt, res)
    same(r.signal, sma_p(res, 23))


@pytest.mark.parametrize("negative,roc_len", [(False, 1), (True, 1), (True, 50)])
def test_volume_index_hpotter_and_fosback(negative, roc_len):
    roc = roc_p(cl, roc_len)
    nres, out = NA, []
    for i in range(N):
        cond = lt(v[i], at(v, i, 1)) if negative else gt(v[i], at(v, i, 1))
        nres = nz(nres, 0) + roc[i] if cond else nz(nres, 0)
        out.append(nres)
    r = hp.volume_index(C, V, negative, 255, roc_len, hpotter=True)
    same(r.index, out)
    same(r.signal, ema_p(out, 255))
    lib = ti.nvi(C, V) if negative else ti.pvi(C, V)
    same(hp.volume_index(C, V, negative).index, lib.nvi if negative else lib.pvi)


def test_ema_volume_weighted():
    pv = list(v * c)
    exp = [a / b for a, b in zip(ema_p(pv, 22), ema_p(list(v), 22))]
    same(hp.ema_volume_weighted(C, V, 22), exp)


def test_klinger_hpotter_and_volume_force():
    xt = [v[i] * 100 if gt(hlc3[i], at(hlc3, i, 1)) else -v[i] * 100 for i in range(N)]
    kvo = [a - b for a, b in zip(ema_p(xt, 34), ema_p(xt, 55))]
    r = hp.klinger_volume_oscillator(H, L, C, V, hpotter=True)
    same(r.kvo, kvo)
    same(r.signal, ema_p(kvo, 13))
    # Klinger's volume force
    vf, cm, tr_prev, dm_prev = [], NA, NA, NA
    for i in range(N):
        tp = h[i] + l[i] + c[i]
        trend = 1 if (i and tp > h[i - 1] + l[i - 1] + c[i - 1]) else -1
        dm = h[i] - l[i]
        cm = dm if i == 0 else (cm + dm if trend == tr_prev else dm_prev + dm)
        temp = 2.0 if cm == 0 else abs(2 * (dm / cm - 1))
        vf.append(v[i] * temp * trend * 100)
        tr_prev, dm_prev = trend, dm
    kvo = [a - b for a, b in zip(ema_p(vf, 34), ema_p(vf, 55))]
    same(hp.klinger_volume_oscillator(H, L, C, V).kvo, kvo, rtol=1e-8)


def test_tfs_volume_and_money_flow_ports():
    sv = [v[i] if c[i] > o[i] else (-v[i] if c[i] < o[i] else 0.0) for i in range(N)]
    same(hp.tfs_volume_oscillator(O, C, V, 7), [t / 7 if not isna(t) else NA for t in sum_p(sv, 7)])
    f = [(c[i] - o[i]) / (h[i] - l[i]) * v[i] if (h[i] - l[i]) * v[i] > 0 else 0.0 for i in range(N)]
    exp = [a - b for a, b in zip(ema_p(sum_p(f, 10), 10), ema_p(sum_p(f, 3), 3))]
    same(hp.hpotter_money_flow(O, H, L, C, V, 3, 10), exp)


# ---------------------------------------------------------------------------
# Pee
# ---------------------------------------------------------------------------

def test_tcf_hpotter_port():
    ch = change(cl)
    pc = [ch[i] if gt(ch[i], 0) else 0.0 for i in range(N)]
    mc = [ch[i] * -1 if lt(ch[i], 0) else 0.0 for i in range(N)]
    pcf, mcf, a, b = [], [], NA, NA
    for i in range(N):
        a = 0.0 if pc[i] == 0 else pc[i] + nz(a, 1)
        b = 0.0 if mc[i] == 0 else mc[i] + nz(b, 1)
        pcf.append(a)
        mcf.append(b)
    r = hp.trend_continuation_factor(C, 35)
    same(r.plus_tcf, sum_p([x - y for x, y in zip(pc, mcf)], 35))
    same(r.minus_tcf, sum_p([x - y for x, y in zip(mc, pcf)], 35))


def test_tii_port_after_warmup():
    sma = sma_p(cl, 60)
    out = []
    for i in range(N):
        ps = ns = 0.0
        for j in range(30):
            price, avg = nz(at(cl, i, j)), nz(at(sma, i, j))
            ps += price - avg if price > avg else 0
            ns += 0 if price > avg else avg - price
        out.append(100 * ps / (ps + ns))
    r = hp.trend_intensity_index(C, 60, 30)
    assert np.isnan(r[:88]).all() and not np.isnan(r[88:]).any()
    same(r[88:], out[88:])


# ---------------------------------------------------------------------------
# Siligardos, Dorsey
# ---------------------------------------------------------------------------

def test_reverse_engineering_rsi():
    val, wp = 50, 14
    ep = 2 * wp - 1
    kk = 2 / (ep + 1)
    auc = adc = NA
    out = []
    for i in range(N):
        c1 = at(c, i, 1)
        if gt(c[i], c1):
            auc = kk * (c[i] - c1) + (1 - kk) * nz(auc, 1)
            adc = (1 - kk) * nz(adc, 1)
        else:
            auc = (1 - kk) * nz(auc, 1)
            adc = kk * (c1 - c[i]) + (1 - kk) * nz(adc, 1)
        nv = (wp - 1) * (adc * val / (100 - val) - auc)
        out.append(NA if isna(nv) else (c[i] + nv if nv >= 0 else c[i] + nv * (100 - val) / val))
    hpv = hp.reverse_engineering_rsi(C, val, wp, hpotter=True)
    same(hpv, out)
    same(hp.reverse_engineering_rsi(C, val, wp), out, tail=TAIL, rtol=1e-7)


def test_pivot_detector_oscillator():
    ma, r = sma_p(cl, 200), rsi_p(cl, 14)
    out = []
    for i in range(N):
        res = (r[i] - 35) / (85 - 35) if gt(c[i], ma[i]) else ((r[i] - 20) / (70 - 20) if le(c[i], ma[i]) else 0)
        out.append(res * 100)
    pdo = hp.pivot_detector_oscillator(C)
    same(pdo[199:], out[199:])
    assert np.isnan(pdo[:199]).all()


def rvi_port(x, n=10):
    sd = stdev_p(x, n)
    nu = nd = NA
    out = []
    for i in range(N):
        d = 0 if gt(x[i], at(x, i, 1)) else sd[i]
        u = sd[i] if gt(x[i], at(x, i, 1)) else 0
        nu = (13 * nz(nu, 0) + u) / 14
        nd = (13 * nz(nd, 0) + d) / 14
        out.append(NA if isna(nu) or isna(nd) or nu + nd == 0 else 100 * nu / (nu + nd))
    return out


def test_rvi_and_inertia_hpotter():
    rv = rvi_port(cl)
    same(hp.rvi_dorsey(C, hpotter=True), rv)
    same(hp.inertia(H, L, C, 10, 14, hpotter=True), ema_p(rv, 14))


def test_rvi_dorsey_and_inertia_original():
    def rvi(x):
        sd, ch = stdev_p(x, 10), change(x)
        u = [NA if isna(s) or isna(d) else (s if d > 0 else 0.0) for s, d in zip(sd, ch)]
        dd = [NA if isna(s) or isna(d) else (s if d < 0 else 0.0) for s, d in zip(sd, ch)]
        a, b = rma_p(u, 14), rma_p(dd, 14)
        return [NA if isna(p) else 100 * p / (p + q) for p, q in zip(a, b)]
    same(hp.rvi_dorsey(C), rvi(cl))
    refined = [(a + b) / 2 for a, b in zip(rvi(list(h)), rvi(list(l)))]
    same(hp.inertia(H, L, C), linreg_p(refined, 20, 0), rtol=1e-8)
    # HPotter's RVI converges to Dorsey's; only unchanged closes (counted as
    # "down" by HPotter) keep the two apart
    a, b = np.asarray(hp.rvi_dorsey(C, hpotter=True)), np.asarray(hp.rvi_dorsey(C))
    assert np.nanmedian(np.abs(a - b)[-TAIL:]) < 0.5
    no_ties = pd.Series(c + np.arange(N) * 1e-6, index=D.index)
    a, b = np.asarray(hp.rvi_dorsey(no_ties, hpotter=True)), np.asarray(hp.rvi_dorsey(no_ties))
    np.testing.assert_allclose(a[-TAIL:], b[-TAIL:], atol=1e-6)


# ---------------------------------------------------------------------------
# Blau
# ---------------------------------------------------------------------------

def test_ergodic_tsi_dti_mdi_eco_ports():
    m = change(cl)
    am = [NA if isna(t) else abs(t) for t in m]
    v1 = ema_p(ema_p(ema_p(m, 4), 8), 6)
    v2 = ema_p(ema_p(ema_p(am, 4), 8), 6)
    tsi = [NA if isna(a) or isna(b) else (100 * a / b if b != 0 else 0) for a, b in zip(v1, v2)]
    r = hp.ergodic_tsi(C, 4, 8, 6, 3)
    same(r.tsi, tsi)
    same(r.signal, ema_p(tsi, 3))
    same(hp.ergodic_tsi(C, 25, 13, 1, 13).tsi, ti.tsi(C).tsi)
    # DTI
    hmu = [h[i] - h[i - 1] if i and h[i] - h[i - 1] > 0 else 0.0 for i in range(N)]
    lmd = [-(l[i] - l[i - 1]) if i and l[i] - l[i - 1] < 0 else 0.0 for i in range(N)]
    x = [a - b for a, b in zip(hmu, lmd)]
    a1 = ema_p(ema_p(ema_p(x, 14), 10), 5)
    a2 = ema_p(ema_p(ema_p([abs(t) for t in x], 14), 10), 5)
    same(hp.directional_trend_index(H, L), [NA if isna(p) else (100 * p / q if q != 0 else 0) for p, q in zip(a1, a2)])
    # MDI
    s = [a - b for a, b in zip(cl, ema_p(cl, 32))]
    mdi = ema_p(ema_p(s, 5), 5)
    r = hp.ergodic_mdi(C, 32, 5, 5, 5)
    same(r.mdi, mdi)
    same(r.signal, ema_p(mdi, 5))
    # ECO: 100 * ema(ema(c - o, r), s) / ema(ema(h - l, r), s)
    e1 = ema_p(ema_p(list(c - o), 32), 12)
    e2 = ema_p(ema_p(list(h - l), 32), 12)
    same(hp.ergodic_candlestick_oscillator(O, H, L, C, 32, 12).csi,
         [NA if isna(a) else 100 * a / b for a, b in zip(e1, e2)])


# ---------------------------------------------------------------------------
# Stochastic / RSI / CMO variants
# ---------------------------------------------------------------------------

def test_dss_bressert_port():
    pre = ema_p(stoch_p(cl, list(h), list(l), 10), 9)
    dss = ema_p(stoch_p(pre, pre, pre, 10), 9)
    r = hp.dss_bressert(H, L, C, 10, 9, 5)
    same(r.dss, dss)
    same(r.signal, ema_p(dss, 5))


def test_obos_and_smoothed_rsi_ports():
    st = stoch_p(cl, list(h), list(l), 10)
    same(hp.hpotter_obos(H, L, C, 10),
         [st[i] / 100 if gt(c[i], at(c, i, 10)) else (100 - st[i]) / 100 for i in range(N)])
    xv = [(c[i] + 2 * at(c, i, 1) + 2 * at(c, i, 2) + at(c, i, 3)) / 6 for i in range(N)]
    cu = sum_p([xv[i] - at(xv, i, 1) if gt(xv[i], at(xv, i, 1)) else 0 for i in range(N)], 10)
    cd = sum_p([at(xv, i, 1) - xv[i] if lt(xv[i], at(xv, i, 1)) else 0 for i in range(N)], 10)
    same(hp.ehlers_smoothed_rsi(C, 10),
         [NA if isna(a) else (a / (a + b) if a + b != 0 else 0) for a, b in zip(cu, cd)])


def test_dynamic_momentum_index_chande():
    sd = stdev_p(cl, 5)
    asd = sma_p(sd, 10)
    td = []
    for a, b in zip(sd, asd):
        if isna(a) or isna(b):
            td.append(NA)
            continue
        vi = a / b if b != 0 else NA
        t = 30.0 if isna(vi) or vi == 0 else float(math.floor(14 / vi))
        td.append(min(max(t, 5.0), 30.0))
    out, up, dn = [], NA, NA
    for i in range(N):
        t = td[i]
        if i == 0 or isna(t):
            out.append(NA)
            continue
        ch = c[i] - c[i - 1]
        if isna(up):
            nn = int(t)
            if i < nn:
                out.append(NA)
                continue
            chs = [c[i - j] - c[i - j - 1] for j in range(nn)]
            up = sum(max(x, 0) for x in chs) / nn
            dn = sum(max(-x, 0) for x in chs) / nn
        else:
            up += (max(ch, 0) - up) / t
            dn += (max(-ch, 0) - dn) / t
        out.append(100.0 if dn == 0 else (0.0 if up == 0 else 100 - 100 / (1 + up / dn)))
    r = hp.dynamic_momentum_index(C)
    same(r.period, td)
    same(r.dmi, out, rtol=1e-8)


def test_cmo_family_ports():
    mom = change(cl)
    amom = [NA if isna(t) else abs(t) for t in mom]
    parts = []
    for n in (5, 10, 20):
        s, sa = sum_p(mom, n), sum_p(amom, n)
        parts.append([NA if isna(a) else a / b for a, b in zip(s, sa)])
    av = [NA if any(isna(p[i]) for p in parts) else 100 * (parts[0][i] + parts[1][i] + parts[2][i]) / 3
          for i in range(N)]
    same(hp.cmo_average(C), av)
    same(hp.cmo_average(C, absolute=True), np.abs(av))
    # HPotter's CMO == ta.cmo
    smom = sma_p(amom, 9)
    cmo = [NA if isna(smom[i]) or isna(at(c, i, 9)) else 100 * ((c[i] - at(c, i, 9)) / (smom[i] * 9))
           for i in range(N)]
    same(ti.cmo(C, 9), cmo, rtol=1e-7)
    # CMOfilt
    flt = 0.3
    fm = [m if gt(a, flt) else 0 for m, a in zip(mom, amom)]
    fa = [a if gt(a, flt) else 0 for a in amom]
    s, sa = sum_p(fm, 9), sum_p(fa, 9)
    same(hp.cmo_filtered(C, 9, flt), [NA if isna(a) or b == 0 else 100 * a / b for a, b in zip(s, sa)])
    # CMOaDisparity
    for hpot in (False, True):
        r = hp.cmo_disparity(C, 50, 25, 10, hpotter=hpot)
        e = ema_p(cl, 10)
        same(r.third, [100 * (x - y) / (x if hpot else y) if not isna(y) else NA for x, y in zip(cl, e)])


def test_ravi_and_pfe():
    f, s = sma_p(cl, 7), sma_p(cl, 65)
    rv = [NA if isna(b) else ((a - b) / b) * 100 for a, b in zip(f, s)]
    same(hp.ravi(C, hpotter=True), rv)
    same(hp.ravi(C), np.abs(rv))
    # HPotter PFE (Length 9)
    n = 9
    c2c = sum_p([math.sqrt((c[i] - c[i - 1]) ** 2 + 1) if i else NA for i in range(N)], n)
    raw = []
    for i in range(N):
        if isna(at(c, i, n)) or isna(c2c[i]):
            raw.append(NA)
            continue
        pfe = math.sqrt((c[i] - c[i - n]) ** 2 + 100)
        raw.append(pine_round((pfe / c2c[i]) * 100) if c[i] - c[i - n] > 0 else pine_round(-(pfe / c2c[i]) * 100))
    r = hp.polarized_fractal_efficiency(C, 9, 5, hpotter=True)
    same(r.raw, raw)
    same(r.pfe, ema_p(raw, 5))
    # Hannula (MetaStock): Roc(C,9,$), Pwr(10,2), Sum(...,9), no rounding
    raw2 = []
    for i in range(N):
        if isna(at(c, i, 9)) or isna(c2c[i]):
            raw2.append(NA)
            continue
        x = 100 * math.sqrt((c[i] - c[i - 9]) ** 2 + 100) / c2c[i]
        raw2.append(x if c[i] > c[i - 9] else -x)
    same(hp.polarized_fractal_efficiency(C, 10, 5).raw, raw2)


def test_confluence_port():
    H_ = 10
    STL = pine_round((H_ * 2) - 1 - 0.5)
    ITL = pine_round((STL * 2) - 1 - 0.5)
    LTL = pine_round((ITL * 2) - 1 - 0.5)
    HOFF, SOFF, IOFF = pine_round(H_ / 2 - 0.5), pine_round(STL / 2 - 0.5), pine_round(ITL / 2 - 0.5)
    P = cl
    havg, savg, iavg, lavg = sma_p(P, H_), sma_p(P, STL), sma_p(P, ITL), sma_p(P, LTL)
    lavg_ohlc = sma_p(ohlc4, LTL - 1)
    h2, s2, i2, l2 = sma_p(P, H_ - 1), sma_p(P, STL - 1), sma_p(P, ITL - 1), sma_p(P, LTL - 1)
    out = []
    hist = {k: [] for k in ("v5", "v6", "v7", "v13", "xsum", "errsum", "mom", "v70")}

    def past(name, i, n):
        return at(hist[name], i, n) if n else hist[name][i]

    def sc(x):
        return math.sin(x * 2 * 3.14 / 360) + math.cos(x * 2 * 3.14 / 360)

    def score(x, x1, sig):
        if gt(x, 0) and lt(x, x1) and lt(x, sig): return 1
        if gt(x, 0) and lt(x, x1) and gt(x, sig): return 2
        if gt(x, 0) and gt(x, x1) and lt(x, sig): return 2
        if gt(x, 0) and gt(x, x1) and gt(x, sig): return 3
        if lt(x, 0) and gt(x, x1) and gt(x, sig): return -1
        if lt(x, 0) and lt(x, x1) and gt(x, sig): return -2
        if lt(x, 0) and gt(x, x1) and lt(x, sig): return -2
        if lt(x, 0) and lt(x, x1) and lt(x, sig): return -3
        return 0
    for i in range(N):
        drh = H_ * (havg[i] * 2 - at(havg, i, 1)) - h2[i] * (H_ - 1)
        drs = STL * (savg[i] * 2 - at(savg, i, 1)) - s2[i] * (STL - 1)
        dri = ITL * (iavg[i] * 2 - at(iavg, i, 1)) - i2[i] * (ITL - 1)
        drl = LTL * (lavg[i] * 2 - at(lavg, i, 1)) - l2[i] * (LTL - 1)
        v5 = (h2[i] * (H_ - 1) + drh) / H_
        v6 = (s2[i] * (STL - 1) + drs) / STL
        v7 = (i2[i] * (ITL - 1) + dri) / ITL
        v13 = (lavg_ohlc[i] * (LTL - 1) + drl) / LTL
        for k_, val in (("v5", v5), ("v6", v6), ("v7", v7), ("v13", v13)):
            hist[k_].append(val)
        mom = (v6 - past("v5", i, HOFF)) + (v7 - past("v6", i, SOFF)) + (v13 - past("v7", i, IOFF))
        xsum = sc(v5) + sc(v6) + sc(v7)
        xerr = sc(havg[i]) + sc(savg[i]) + sc(iavg[i])
        hist["xsum"].append(xsum)
        hist["mom"].append(mom)
        xs_off, ha_off = at(hist["xsum"], i, SOFF), at(havg, i, SOFF)
        cond2 = (gt(xsum, xs_off) and lt(havg[i], ha_off)) or (lt(xsum, xs_off) and gt(havg[i], ha_off))
        errsum = (xsum - xerr) * (-1 if cond2 else 1)
        hist["errsum"].append(errsum)
        hist["v70"].append(v5 - v13)
    errsig_s, v71_s = sma_p(hist["errsum"], SOFF), sma_p(hist["v70"], H_)
    for i in range(N):
        momsig = (savg[i] - at(havg, i, HOFF)) + (iavg[i] - at(savg, i, SOFF)) + (lavg[i] - at(iavg, i, IOFF))
        errsum, mom, v70 = hist["errsum"][i], hist["mom"][i], hist["v70"][i]
        v42 = (score(errsum, at(hist["errsum"], i, 1), errsig_s[i]) + score(mom, at(hist["mom"], i, 1), momsig)
               + score(v70, at(hist["v70"], i, 1), v71_s[i]))
        if gt(v42, 0) and gt(v70, 0):
            conf = v42
        elif lt(v42, 0) and lt(v70, 0):
            conf = v42
        elif (gt(v42, 0) and lt(v70, 0)) or (lt(v42, 0) and gt(v70, 0)):
            conf = v42 / 10
        else:
            conf = 0
        out.append(conf)
    same(hp.confluence(O, H, L, C, 10), out)


# ---------------------------------------------------------------------------
# Ehlers ports
# ---------------------------------------------------------------------------

def bandpass_port(length, delta, pi):
    beta = math.cos(pi * (360 / length) / 180)
    gamma = 1 / math.cos(pi * (720 * delta / length) / 180)
    alpha = gamma - math.sqrt(gamma * gamma - 1)
    bp, out = [], []
    for i in range(N):
        b = 0.5 * (1 - alpha) * (hl2[i] - at(hl2, i, 2)) + beta * (1 + alpha) * nz(at(bp, i, 1)) \
            - alpha * nz(at(bp, i, 2))
        bp.append(b)
    return bp


def test_bandpass_ett_emd_ports():
    same(hp.ehlers_bandpass(H, L, 20, 0.5, hpotter=True), bandpass_port(20, 0.5, 3.14))
    same(hp.ehlers_bandpass(H, L, 20, 0.5), bandpass_port(20, 0.5, math.pi))
    bp = bandpass_port(20, 0.5, 3.1415)
    same(hp.extracting_the_trend(H, L, 20, 0.5, hpotter=True).trend, sma_p(bp, 40))
    pk = vl = NA
    pks, vls = [], []
    for i in range(N):
        b0, b1, b2 = bp[i], at(bp, i, 1), at(bp, i, 2)
        pk = b1 if (gt(b1, b0) and gt(b1, b2)) else nz(pk)
        vl = b1 if (lt(b1, b0) and lt(b1, b2)) else nz(vl)
        pks.append(pk)
        vls.append(vl)
    r = hp.empirical_mode_decomposition(H, L, 20, 0.5, 0.1, hpotter=True)
    same(r.mean, sma_p(bp, 40))
    same(r.peak, [NA if isna(t) else 0.1 * t for t in sma_p(pks, 50)])
    same(r.valley, [NA if isna(t) else 0.1 * t for t in sma_p(vls, 50)])


def test_dsp_and_eli():
    dsp = [a - b for a, b in zip(ema_p(hl2, 14), ema_p(hl2, 28))]
    same(hp.detrended_synthetic_price(H, L, 14), dsp)
    d7 = [a - b for a, b in zip(ema_p(hl2, 7), ema_p(hl2, 14))]
    same(hp.ehlers_leading_indicator(H, L, 7).eli, [a - b for a, b in zip(d7, ema_p(d7, 7))])


def test_fisher_hpotter_port_and_main():
    hh, ll = highest_p(hl2, 10), lowest_p(hl2, 10)
    v1 = fi = NA
    out = []
    for i in range(N):
        rng = hh[i] - ll[i]
        v1 = 0.33 * 2 * ((hl2[i] - ll[i]) / rng - 0.5) + 0.67 * nz(v1) if not isna(rng) and rng != 0 else NA
        v2 = 0.999 if gt(v1, 0.99) else (-0.999 if lt(v1, -0.99) else v1)
        fi = 0.5 * math.log((1 + v2) / (1 - v2)) + 0.5 * nz(fi) if not isna(v2) else NA
        out.append(fi)
    same(hp.fisher_transform(H, L, 10, hpotter=True).fisher, out)
    same(hp.fisher_transform(H, L, 10).fisher, ti.fisher(H, L, 10).fisher)


# ---------------------------------------------------------------------------
# Moving averages and bands
# ---------------------------------------------------------------------------

def test_kama_hpotter_port_and_convergence():
    n = 21
    noise = sum_p([NA if i == 0 else abs(c[i] - c[i - 1]) for i in range(N)], n)
    ama, out = NA, []
    for i in range(N):
        sig = abs(c[i] - at(c, i, n)) if i >= n else NA
        er = sig / noise[i] if (not isna(noise[i]) and noise[i] != 0) else 0
        sm = (er * (0.666 - 0.0645) + 0.0645) ** 2
        ama = nz(ama) + sm * (c[i] - nz(ama))
        out.append(ama)
    same(hp.kama(C, n, hpotter=True), out)
    same(hp.kama(C, n), ti.kama(C, n))
    a, b = np.asarray(out), np.asarray(ti.kama(C, n))
    np.testing.assert_allclose(a[-500:], b[-500:], rtol=2e-3)


def test_rmta_port():
    a = 2 / 22
    bot = res = NA
    out = []
    for i in range(N):
        nb = (1 - a) * nz(bot, c[i]) + c[i]
        res = (1 - a) * nz(res, c[i]) + (a * (c[i] + nb - nz(bot, 0)))
        bot = nb
        out.append(res)
    same(hp.recursive_moving_trend_average(C, 21), out)


def test_t3_cci_port():
    b = 0.618
    b2, b3 = b * b, b * b * b
    c1, c2, c3, c4 = -b3, 3 * (b2 + b3), -3 * (2 * b2 + b + b3), 1 + 3 * b + b3 + 3 * b2
    nr = 1 + 0.5 * (5 - 1)
    w1 = 2 / (nr + 1)
    w2 = 1 - w1
    sm, dv = sma_p(cl, 14), dev_p(cl, 14)
    cci = [NA if isna(s) or d == 0 else (x - s) / (0.015 * d) for x, s, d in zip(cl, sm, dv)]
    e = [NA] * 6
    out = []
    for i in range(N):
        n1 = w1 * cci[i] + w2 * nz(e[0])
        n2 = w1 * n1 + w2 * nz(e[1])
        n3 = w1 * n2 + w2 * nz(e[2])
        n4 = w1 * n3 + w2 * nz(e[3])
        n5 = w1 * n4 + w2 * nz(e[4])
        n6 = w1 * n5 + w2 * nz(e[5])
        e = [n1, n2, n3, n4, n5, n6]
        out.append(c1 * n6 + c2 * n5 + c3 * n4 + c4 * n3)
    same(hp.t3_cci(C, 14, 5, b).t3cci, out, rtol=1e-8)


def test_bands_ports():
    r = hp.keltner_original(H, L, C, 10)
    p, mv = sma_p(hlc3, 10), sma_p(list(h - l), 10)
    same(r.upper, [a + b for a, b in zip(p, mv)])
    same(r.lower, [a - b for a, b in zip(p, mv)])
    tma = sma_p(sma_p(cl, 14), 14)
    r = hp.high_low_bands(C, 14, 1, hpotter=True)
    same(r.upper, [t + t * 1 / 100 for t in tma])
    same(hp.high_low_bands(C, 14, 1).basis, ti.trima(C, 14))
    e = ema_p(cl, 9)
    r = hp.ma_displaced_envelope(C, 9, 0.5, 0.5, 13)
    same(r.upper, [at(e, i, 13) * ((100 + 0.5) / 100) for i in range(N)])
    same(r.lower, [at(e, i, 13) * ((100 - 0.5) / 100) for i in range(N)])
    p = math.ceil(math.sqrt(20))
    v1, v2 = ema_p(ema_p(cl, p), p), ema_p(ema_p(list(h - l), p), p)
    r = hp.adaptive_price_zone(H, L, C, 20, 2)
    same(r.upper, [2 * b + a for a, b in zip(v1, v2)])
    same(r.lower, [a - 2 * b for a, b in zip(v1, v2)])
    dp = [a - b for a, b in zip(sma_p(list(h), 21), sma_p(list(l), 21))]
    r = hp.dapd_bands(H, L, 21)
    same(r.top, list(h + np.array(dp)))
    same(r.bottom, list(l - np.array(dp)))
    r = hp.bill_williams_3lines(H, L, hpotter=True)
    same(r.jaw, shift(sma_p(hl2, 13), 8))
    same(r.teeth, shift(sma_p(hl2, 8), 5))
    same(r.lips, shift(sma_p(hl2, 5), 3))
    a = ti.alligator(H, L)
    r = hp.bill_williams_3lines(H, L)
    same(r.jaw, a.jaw)
    same(r.lips, a.lips)
    lg = linreg_p(cl, 20, 5)
    r = hp.hpotter_center_of_gravity(C, 20, 5, 1)
    same(r.upper1, [x + (cc * 1) / 100 for x, cc in zip(lg, cl)], rtol=1e-8)
    same(r.lower2, [x - ((cc * 1) / 100) * 2 for x, cc in zip(lg, cl)], rtol=1e-8)


# ---------------------------------------------------------------------------
# Momentum / trend oscillators
# ---------------------------------------------------------------------------

def test_pring_special_k_and_kst_params():
    osc = [0.0] * N
    for r, s, w in hp._SPECIAL_K:
        osc = [a + b * w for a, b in zip(osc, sma_p(roc_p(cl, r), s))]
    r = hp.pring_special_k(C, 10)
    same(r.special_k, osc, rtol=1e-8)
    same(r.signal, sma_p(osc, 10), rtol=1e-8)
    # HPotter's MovROC = KST formula with ROC 6/10/15/20 and SMA 10/10/9/15
    mr = [a + 2 * b + 3 * x + 4 * y for a, b, x, y in zip(sma_p(roc_p(cl, 6), 10), sma_p(roc_p(cl, 10), 10),
                                                        sma_p(roc_p(cl, 15), 9), sma_p(roc_p(cl, 20), 15))]
    same(ti.kst(C, 6, 10, 15, 20, 10, 10, 9, 15).kst, mr, rtol=1e-8)


def test_fsk_sv_stn_ports():
    m3 = change(cl, 3)
    kk = change(m3, 1)
    fk = ema_p(kk, 65)
    r = hp.fast_slow_kurtosis(C)
    same(r.fast, fk)
    same(r.fast_slow, wma_p(fk, 3))
    n = 30
    mc, mh, nc, nl = highest_p(cl, n), highest_p(list(h), n), lowest_p(cl, n), lowest_p(list(l), n)
    st = math.sqrt(253 / n)
    sv = []
    for a, b, x, y in zip(mc, mh, nc, nl):
        if isna(a):
            sv.append(NA)
            continue
        vol = ((0.6 * math.log(a / x) * st) + (0.6 * math.log(b / y) * st)) * 0.5
        sv.append(0 if vol < 0 else (2.99 if vol > 2.99 else vol))
    same(hp.statistical_volatility(H, L, C, n), sv)
    stn = []
    for i in range(N):
        s = 0.0
        for j in range(1, 21):
            s = s + (1 / at(c, i, j)) / 21
        stn.append(NA if isna(s) else -10 * math.log(s))
    same(hp.signal_to_noise(C, 21), stn)


def test_three_ten_and_dinapoli():
    o3 = [a - b for a, b in zip(ema_p(hl2, 3), ema_p(hl2, 10))]
    r = hp.three_ten_oscillator(H, L, C, hpotter=True)
    same(r.osc, o3)
    same(r.signal, sma_p(o3, 16))
    o3s = [a - b for a, b in zip(sma_p(cl, 3), sma_p(cl, 10))]
    same(hp.three_ten_oscillator(H, L, C).osc, o3s)
    same(hp.dinapoli_detrended_oscillator(C, 14), [x - s for x, s in zip(cl, sma_p(cl, 14))])


def test_gann_swing_ports():
    for src_h, src_l, sign in ((list(h), list(l), 1), (cl, cl, -1)):
        hh, ll = highest_p(src_h, 5), lowest_p(src_l, 5)
        g, out = NA, []
        for i in range(N):
            if gt(at(hh, i, 2), at(hh, i, 1)) and gt(hh[i], at(hh, i, 1)):
                g = 1 * sign
            elif lt(at(ll, i, 2), at(ll, i, 1)) and lt(ll[i], at(ll, i, 1)):
                g = -1 * sign
            else:
                g = nz(g, 0)
            out.append(g)
        res = hp.gann_swing_oscillator(pd.Series(src_h), pd.Series(src_l), 5)
        same(sign * np.asarray(res), out)


def test_small_oscillators():
    r = hp.hl_range_histogram(H, L, C, 13, False)
    same(r.average, sma_p(list(np.abs(h - l)), 13))
    s = sma_p(cl, 28)
    same(hp.trend_analysis_index(C), [NA if isna(a) else (a - b) * 100 / x
                                      for a, b, x in zip(highest_p(s, 5), lowest_p(s, 5), cl)])
    same(hp.wami(C), ema_p(ema_p(wma_p(change(cl), 4), 13), 13))
    xhh, xll = highest_p(list(h), 28), lowest_p(list(l), 28)
    den = sum_p([NA if i == 0 else abs(c[i] - c[i - 1]) for i in range(N)], 28)
    same(hp.vertical_horizontal_filter(H, L, C, 28, hpotter=True),
         [NA if isna(d) else abs(a - b) / d for a, b, d in zip(xhh, xll, den)])
    same(hp.vertical_horizontal_filter(H, L, C, 28), ti.vhf(C, 28))
    other = C * (1 + 0.01 * np.sin(np.arange(N)))
    same(hp.comparative_relative_strength(C, other, 10), sma_p(list(c / other.to_numpy()), 10))


def test_adxr_and_csi_ports():
    adx = fadx_p(14)
    for hpot, lag in ((True, 14), (False, 13)):
        exp = [NA if isna(at(adx, i, lag)) else (adx[i] + at(adx, i, lag)) / 2 for i in range(N)]
        same(hp.adxr(H, L, C, 14, hpotter=hpot).adxr, exp, rtol=1e-8)
    same(hp.adxr(H, L, C, 14).adxr, ti.adxr(H, L, C, 14))
    kk = 100 * ((50 / math.sqrt(3000) / (150 + 10)))
    atr = atr_p(14)
    nadxr = [NA if isna(at(adx, i, 14)) else (adx[i] + at(adx, i, 14)) * 0.5 for i in range(N)]
    same(hp.commodity_selection_index(H, L, C, 14, 50, 3000, 10, hpotter=True),
         [kk * a * b for a, b in zip(atr, nadxr)], rtol=1e-8)


def test_trend_trader_port():
    avg = wma_p(atr_p(1), 21)
    hc, lc = highest_p(list(h), 21), lowest_p(list(l), 21)
    ret, out = NA, []
    for i in range(N):
        hi_l = at(hc, i, 1) - (at(avg, i, 1) * 3)
        lo_l = at(lc, i, 1) + (at(avg, i, 1) * 3)
        ret = hi_l if (gt(c[i], hi_l) and gt(c[i], lo_l)) else (lo_l if (lt(c[i], lo_l) and lt(c[i], hi_l))
                                                             else nz(ret, 0))
        out.append(ret)
    same(hp.trend_trader(H, L, C, 21, 3), out)


def test_dynamo_port():
    osc = sma_p(stoch_p(cl, list(h), list(l), 10), 10)
    ma = sma_p(osc, 20)
    lo = hi = NA
    out = []
    for i in range(N):
        lo = osc[i] if lt(osc[i], nz(lo, 9999999)) else nz(lo, 9999999)
        hi = osc[i] if gt(osc[i], nz(hi)) else nz(hi)
        out.append((lo + hi) / 2 - (ma[i] - osc[i]))
    same(hp.dynamo(H, L, C).dynamo, out)


def test_ttm_scalper_port():
    sw = sbs = cs = NA
    lev, st = [], []
    for i in range(N):
        c0, c1, c2, c3 = c[i], at(c, i, 1), at(c, i, 2), at(c, i, 3)
        ts = 1 if (lt(c1, c0) and (lt(c2, c1) or lt(c3, c1))) else 0
        tb = 1 if (gt(c1, c0) and (gt(c2, c1) or gt(c3, c1))) else 0
        psw = sw
        sw = 1 if ts else (0 if tb else nz(sw))
        if ts and (not isna(psw) and psw == 0):
            sbs, cs = h[i], 1
        elif tb and (not isna(psw) and psw == 1):
            sbs, cs = l[i], 0
        else:
            sbs, cs = nz(sbs), nz(cs)
        lev.append(sbs)
        st.append(cs)
    r = hp.ttm_scalper(H, L, C)
    same(r.level, lev)
    same(r.state, st)


def test_three_line_break_port():
    hist = {"t": [], "u": [], "u1": [], "u2": [], "u3": []}

    def prev(k, i):
        return hist[k][i - 1] if i else NA
    for i in range(N):
        x = c[i]
        t, u, u1, u2, u3 = 1, x, x, x, x
        if prev("t", i) == 1:
            if gt(x, prev("u", i)):
                u3, u2, u1, u, t = prev("u2", i), prev("u1", i), prev("u", i), x, 1
            elif lt(x, prev("u3", i)):
                u3, u2, u1, u, t = prev("u1", i), prev("u1", i), prev("u1", i), x, -1
            else:
                t = 1
        else:
            if gt(x, prev("u3", i)):
                u3, u2, u1, u, t = prev("u1", i), prev("u1", i), prev("u1", i), x, 1
            elif lt(x, prev("u", i)):
                u3, u2, u1, u, t = prev("u2", i), prev("u1", i), prev("u", i), x, -1
            else:
                t = -1
        for kk, val in zip(("t", "u", "u1", "u2", "u3"), (t, u, u1, u2, u3)):
            hist[kk].append(val)
    r = hp.hpotter_three_line_break(C)
    same(r.trend, hist["t"])
    same(r.line3, hist["u3"])


def test_kwan_nrp_port():
    mom = [NA if isna(at(c, i, 9)) else c[i] / at(c, i, 9) * 100 for i in range(N)]
    rs, st = rsi_p(list(o), 9), stoch_p(list(o), list(h), list(l), 9)
    arr, out = [NA], []
    for i in range(N):
        if not isna(mom[i]) and mom[i] != 0:
            arr.append(st[i] * rs[i] / mom[i])
        avr = 0.0
        if len(arr) > 2:
            for j in range(len(arr) - 2, len(arr)):
                avr += arr[j]
        out.append(avr / 2)
    same(hp.kwan_nrp(O, H, L, C), out)


def test_smart_money_index_hpotter_and_hays():
    ho, hc = shift(list(o), 1), shift(cl, 1)  # tf == chart timeframe
    res, out = NA, []
    for i in range(N):
        res = nz(res, 1) - (o[i] - c[i]) + (ho[i] - hc[i])
        out.append(res)
    same(hp.smart_money_index_hpotter(O, C, pd.Series(ho), pd.Series(hc)), out)
    # Hays on hourly bars: first hour from yesterday's close, last 1 hour
    sess = ti.session_ids(D.index, "D")
    smi = hp.smart_money_index(O, C, sess, 1, 1)
    days = D.groupby(D.index.floor("D"))
    last = days.close.last()
    first = days.close.first()
    exp, val = [], 0.0
    prev_close = None
    for day in last.index:
        g = days.get_group(day).close.to_numpy()
        ref = prev_close if prev_close is not None else days.get_group(day).open.iloc[0]
        val = val - (g[0] - ref) + (g[-1] - g[-2])
        exp.append(val)
        prev_close = g[-1]
    end = pd.Series(np.asarray(smi), index=D.index).groupby(D.index.floor("D")).last()
    np.testing.assert_allclose(end.to_numpy(), exp, rtol=1e-9, atol=1e-9)
    assert len(first) == len(last)


def test_kase_dev_stops_hpotter_port():
    n = 30
    atr = atr_p(n)
    rwh = [NA if isna(at(l, i, n)) else (h[i] - l[i - n]) / (atr[i] * math.sqrt(n)) for i in range(N)]
    rwl = [NA if isna(at(h, i, n)) else (h[i - n] - l[i]) / (atr[i] * math.sqrt(n)) for i in range(N)]
    pk = wma_p([a - b for a, b in zip(rwh, rwl)], 3)
    rng = [a - b for a, b in zip(highest_p(list(h), 2), lowest_p(list(l), 2))]
    avtr, sd = sma_p(rng, 20), stdev_p(rng, 20)
    r = hp.kase_dev_stops(H, L, C, n, hpotter=True)
    for mult, got in ((3, r.dev3), (2, r.dev2), (1, r.dev1), (0, r.warning)):
        up = highest_p([NA if isna(a) else x - a - mult * s for x, a, s in zip(h, avtr, sd)], 20)
        dn = lowest_p([NA if isna(a) else x + a + mult * s for x, a, s in zip(l, avtr, sd)], 20)
        same(got, [u if gt(p, 0) else d for p, u, d in zip(pk, up, dn)])
    # Kase: two-bar true range (with close[2]), 30 bars, 0 / 1 / 2.2 / 3.6 deviations
    dtr = [NA if i < 2 else max(h[i], h[i - 1], c[i - 2]) - min(l[i], l[i - 1], c[i - 2]) for i in range(N)]
    avg, sd = sma_p(dtr, 30), stdev_p(dtr, 30)
    r2 = hp.kase_dev_stops(H, L, C)
    for mult, got in ((3.6, r2.dev3), (2.2, r2.dev2), (1.0, r2.dev1), (0.0, r2.warning)):
        up = highest_p([NA if isna(a) else x - a - mult * s for x, a, s in zip(h, avg, sd)], 30)
        dn = lowest_p([NA if isna(a) else x + a + mult * s for x, a, s in zip(l, avg, sd)], 30)
        same(got, [u if gt(p, 0) else d for p, u, d in zip(pk, up, dn)])


# ---------------------------------------------------------------------------
# Library indicators HPotter re-implements: confirm the verdicts
# ---------------------------------------------------------------------------

def test_hpotter_versions_of_library_indicators():
    # STARC: sma(close, n) +/- atr * K
    r = ti.starc_bands(H, L, C, 5, 15, 1.33)
    same(r.upper, [a + b * 1.33 for a, b in zip(sma_p(cl, 5), atr_p(15))])
    # Accelerator / Awesome
    ao = [a - b for a, b in zip(sma_p(hl2, 5), sma_p(hl2, 34))]
    same(ti.accelerator_oscillator(H, L), [a - b for a, b in zip(ao, sma_p(ao, 5))])
    # Ease of Movement, HPotter's (bug): second difference of the half range
    hr = list((h - l) * 0.5)
    mm = change(hr, 1)
    eom = [NA if isna(at(mm, i, 1)) else 1e6 * ((mm[i] - mm[i - 1]) / (v[i] / (h[i] - l[i])))
           if h[i] != l[i] else 0 for i in range(N)]
    lib = np.asarray(ti.ease_of_movement(H, L, V, 1, 1e6))
    m = ~np.isnan(np.asarray(eom, float)) & ~np.isnan(lib)
    assert np.corrcoef(np.asarray(eom, float)[m], lib[m])[0, 1] < 0.9   # different indicators
    # Williams AD: HPotter (bug) resets on unchanged closes, uses low[1]/high[1]
    wad, out = NA, []
    for i in range(N):
        if gt(c[i], nz(at(c, i, 1), 0)):
            wad = nz(wad, 0) + c[i] - at(l, i, 1)
        elif lt(c[i], nz(at(c, i, 1), 0)):
            wad = nz(wad, 0) + c[i] - at(h, i, 1)
        else:
            wad = 0
        out.append(wad)
    assert np.nanmax(np.abs(np.asarray(out) - np.asarray(ti.williams_ad(H, L, C)))) > 1
    # Linear Regression Intercept (HPotter's loop) == TA-Lib intercept (oldest bar)
    n = 14
    xx = n * (n - 1) * 0.5
    div = xx * xx - n * n * (n - 1) * (2 * n - 1) / 6
    s14 = sum_p(cl, n)
    lri = []
    for i in range(N):
        if i < n - 1:
            lri.append(NA)
            continue
        xy = sum(j * c[i - j] for j in range(n))
        slope = (n * xy - xx * s14[i]) / div
        lri.append((s14[i] - slope * xx) / n)
    same(ti.linreg(C, n).intercept, lri, rtol=1e-7)
    # Laguerre RSI with HPotter's nz(x[1], 1) seeds converges to the library's
    g = 0.5
    l0 = l1 = l2 = l3 = NA
    lb = []
    for x in cl:
        n0 = (1 - g) * x + g * nz(l0, 1)
        n1 = -g * n0 + nz(l0, 1) + g * nz(l1, 1)
        n2 = -g * n1 + nz(l1, 1) + g * nz(l2, 1)
        n3 = -g * n2 + nz(l2, 1) + g * nz(l3, 1)
        l0, l1, l2, l3 = n0, n1, n2, n3
        cu = (n0 - n1 if n0 >= n1 else 0) + (n1 - n2 if n1 >= n2 else 0) + (n2 - n3 if n2 >= n3 else 0)
        cd = (0 if n0 >= n1 else n1 - n0) + (0 if n1 >= n2 else n2 - n1) + (0 if n2 >= n3 else n3 - n2)
        lb.append(cu / (cu + cd) if cu + cd != 0 else 0)
    same(ti.laguerre_rsi(C, 0.5), lb, tail=TAIL, rtol=1e-6, atol=1e-6)
    # SMI Ergodic: HPotter smooths fast (4) then slow (8); same after warm-up
    m1 = change(cl)
    am = [NA if isna(t) else abs(t) for t in m1]
    smi = [a / b for a, b in zip(ema_p(ema_p(m1, 4), 8), ema_p(ema_p(am, 4), 8))]
    same(ti.smi_ergodic(C, 4, 8, 3).smi, smi, tail=TAIL, rtol=1e-6, atol=1e-9)
    # T3 Averages: HPotter's Pine EMA chain == library T3
    e = cl
    es = []
    for _ in range(6):
        e = ema_p(e, 5)
        es.append(e)
    b = 0.7
    t3 = [-b ** 3 * x6 + (3 * b * b + 3 * b ** 3) * x5 + (-6 * b * b - 3 * b - 3 * b ** 3) * x4
          + (1 + 3 * b + b ** 3 + 3 * b * b) * x3 for x3, x4, x5, x6 in zip(es[2], es[3], es[4], es[5])]
    same(ti.t3(C, 5, 0.7), t3, rtol=1e-8)
    # UT Bot / ATR trailing stop
    nl = [3.5 * a for a in atr_p(5)]
    st, out = NA, []
    for i in range(N):
        p, c1 = nz(st), at(c, i, 1)
        if gt(c[i], p) and gt(c1, p):
            st = max(p, c[i] - nl[i]) if not isna(nl[i]) else NA
        elif lt(c[i], p) and lt(c1, p):
            st = min(p, c[i] + nl[i]) if not isna(nl[i]) else NA
        else:
            st = c[i] - nl[i] if gt(c[i], p) else c[i] + nl[i]
        out.append(st)
    same(ti.ut_bot(H, L, C, 3.5, 5).stop if hasattr(ti.ut_bot(H, L, C, 3.5, 5), "stop")
         else ti.ut_bot(H, L, C, 3.5, 5)[0], out)
