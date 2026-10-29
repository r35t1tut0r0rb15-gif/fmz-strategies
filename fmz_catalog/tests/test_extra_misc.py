"""Tests for fmz_catalog/extra_misc.py.

Each indicator is compared with a literal bar-by-bar Python port of its
reference Pine code (the strategy copies, or the original script where the
copies deviate). Pine built-ins (ta.sma, ta.wma, ta.ema, ta.rsi, ...) come
from tv_indicators, which is tested against TA-Lib and TradingView's own
source; everything the scripts write themselves is ported loop by loop.
"""

import math

import numpy as np
import pandas as pd
import pytest

import fmz_catalog.extra_misc as fm
import tv_indicators as ti
from tv_indicators.tests.test_indicators import C, H, L, N, O, V, c, h, l, o, same, v

NA = math.nan


def isna(x):
    return x is None or (isinstance(x, float) and math.isnan(x))


def nz(x, r=0.0):
    return r if isna(x) else x


def at(x, t, i=0):
    """Pine ``x[i]`` evaluated on bar ``t``."""
    j = t - i
    return x[j] if 0 <= j < len(x) else NA


def gt(a, b):
    return not isna(a) and not isna(b) and a > b


def lt(a, b):
    return not isna(a) and not isna(b) and a < b


def pmax(*a):
    return NA if any(isna(x) for x in a) else max(a)


def pmin(*a):
    return NA if any(isna(x) for x in a) else min(a)


def div(a, b):
    return NA if isna(a) or isna(b) or b == 0 else a / b


def arr(x):
    return np.asarray(x, float)


# ---------------------------------------------------------------------------


def test_volume_rsi_matches_strategy_copies():
    length = 14
    ma_u = ma_d = NA
    out = []
    for t in range(N):
        fv, fv1 = c[t], at(c, t, 1)
        up = abs(fv - fv1) * v[t] if gt(fv, fv1) else 0.0
        dn = abs(fv - fv1) * v[t] if lt(fv, fv1) else 0.0
        ma_u = (up + nz(ma_u * (length - 1) if not isna(ma_u) else NA)) / length
        ma_d = (dn + nz(ma_d * (length - 1) if not isna(ma_d) else NA)) / length
        out.append(100 * div(ma_u, ma_u + ma_d))
    same(fm.volume_rsi(C, V, length), out)


def test_cipher_b_rsimfi():
    x = pd.Series([div(c[t] - o[t], h[t] - l[t]) * 150 for t in range(N)], index=C.index)
    ref = ti.sma(x, 60) - 2.5
    same(fm.cipher_b_rsimfi(O, H, L, C), ref)
    assert np.isfinite(fm.cipher_b_rsimfi(O, H, L, C)).sum() > 1000


@pytest.mark.parametrize("ma_type", ["WMA", "SMA", "EMA"])
def test_redk_vader_matches_v4_source(ma_type):
    length, der_avg, smooth, senti, lb = 10, 5, 3, 20, 20
    vmax = V.rolling(lb).max()
    vmin = V.rolling(lb).min()
    # ta.stoch(v, vmax, vmin, lb) = 100 (v - lowest(vmin, lb)) / (highest(vmax, lb) - lowest(vmin, lb))
    ll = vmin.rolling(lb).min()
    hh = vmax.rolling(lb).max()
    vola = [div(100 * (v[t] - ll.iloc[t]), hh.iloc[t] - ll.iloc[t]) for t in range(N)]
    vola = [x / 100 if not isna(x) else NA for x in vola]
    cc, last = [], NA
    for t in range(N):
        r = (pmax(h[t], at(h, t, 1)) - pmin(l[t], at(l, t, 1))) / 2
        sr = div(c[t] - at(c, t, 1), r)
        rsr = pmax(pmin(sr, 1), -1)
        x = rsr * vola[t] if not (isna(rsr) or isna(vola[t])) else NA
        if not isna(x):
            last = x
        cc.append(last)  # fixnan
    cp = pd.Series([pmax(x, 0) for x in cc], index=C.index)
    cm = pd.Series([-pmin(x, 0) if not isna(x) else NA for x in cc], index=C.index)
    vs = pd.Series(vola, index=C.index)
    ma = {"WMA": ti.wma, "SMA": ti.sma, "EMA": ti.ema}[ma_type]
    avg = ma(vs, length)
    dem = ma(cp, length) / avg
    sup = ma(cm, length) / avg
    adp, asp = 100 * ti.wma(dem, der_avg), 100 * ti.wma(sup, der_avg)
    anp = adp - asp
    r = fm.redk_vader(H, L, C, V, ma_type=ma_type)
    same(r.demand, adp)
    same(r.supply, asp)
    same(r.vader, anp)
    same(r.signal, ti.wma(anp, smooth))
    same(r.sentiment, ti.wma(100 * ti.wma(dem, senti) - 100 * ti.wma(sup, senti), smooth))


def _jdehorty_kernel(src, size, hh, r, x_0):
    out = []
    for t in range(N):
        cw = cum = 0.0
        for i in range(0, size + x_0 + 1):
            y = at(src, t, i)
            w = math.pow(1 + (math.pow(i, 2) / ((math.pow(hh, 2) * 2 * r))), -r)
            cw = cw + y * w if not (isna(cw) or isna(y)) else NA
            cum += w
        out.append(cw / cum if not isna(cw) else NA)
    return out


def test_nadaraya_watson_rq_matches_jdehorty():
    size = len(np.array([c[0]]))  # array.size(array.from(src)) == 1
    r = fm.nadaraya_watson_rq(C)  # h 8, r 8, x_0 25, lag 2
    same(r.yhat1, _jdehorty_kernel(c, size, 8.0, 8.0, 25), rtol=1e-12)
    same(r.yhat2, _jdehorty_kernel(c, size, 6.0, 8.0, 25), rtol=1e-12)
    assert np.isnan(r.yhat1.iloc[25]) and not np.isnan(r.yhat1.iloc[26])


def test_nadaraya_watson_rq_size_reproduces_atr_channel_copy():
    # 2ba8a3e89f43: kernel_regression1(src, h, h) passes h (10) as _size, x_0 = 50, r = 10
    hh, rr, x0, lag = 10, 10, 50, 2
    y1 = fm.nadaraya_watson_rq(C, hh, rr, x0, lag, size=hh).yhat1
    y2 = fm.nadaraya_watson_rq(C, hh - lag, rr, x0, 0, size=hh - lag).yhat1
    same(y1, _jdehorty_kernel(c, hh, hh, rr, x0), rtol=1e-12)
    same(y2, _jdehorty_kernel(c, hh - lag, hh - lag, rr, x0), rtol=1e-12)


def _ferf(x):
    if isna(x):
        return NA
    nT = 1.0 / (1.0 + 0.5 * abs(x))
    nAns = 1.0 - nT * math.exp(-x * x - 1.26551223 + nT * (1.00002368 + nT * (0.37409196 + nT * (0.09678418 + nT * (
        -0.18628806 + nT * (0.27886807 + nT * (-1.13520398 + nT * (1.48851587 + nT * (-0.82215223 + nT * 0.17087277)))))))))
    return nAns if x >= 0 else -nAns


@pytest.mark.parametrize("version", [4, 5])
def test_p_signal_matches_kharevsky(version):
    points = 9
    n = points - 1
    ohlc4 = (O + H + L + C) / 4
    ser = ohlc4.diff()
    sd = ti.stdev(ser, n).to_numpy()
    sm = ti.sma(ser, n).to_numpy()
    raw = []
    for t in range(N):
        if version == 4:
            raw.append(_ferf(sm[t] / sd[t] / math.sqrt(2) if gt(sd[t], 0) else 1.0))
        else:
            raw.append(_ferf(sm[t] / sd[t] / math.sqrt(2)) if gt(sd[t], 0) else (NA if isna(sm[t]) else float(np.sign(sm[t]))))
    r = fm.p_signal(ohlc4, points, version)
    same(r.raw, raw, rtol=1e-12)
    same(r.psignal, ti.sma(pd.Series(raw, index=C.index), n), rtol=1e-12)
    assert abs(math.erf(0.3) - _ferf(0.3)) < 2e-7


def _mgs_pinv(A, nrows, ncols):
    """tbiktag's qr_diag + pinv: modified Gram-Schmidt QR, then R^-1 Q^T."""
    Q = [[0.0] * ncols for _ in range(nrows)]
    R = [[0.0] * ncols for _ in range(ncols)]
    for kk in range(ncols):
        a = [A[i][kk] for i in range(nrows)]
        for j in range(kk):
            rr = sum(Q[i][j] * a[i] for i in range(nrows))
            R[j][kk] = rr
            a = [a[i] - rr * Q[i][j] for i in range(nrows)]
        rr = math.sqrt(sum(x * x for x in a))
        R[kk][kk] = rr
        for i in range(nrows):
            Q[i][kk] = a[i] / rr
    Rinv = [[0.0] * ncols for _ in range(ncols)]
    Rinv[0][0] = 1 / R[0][0]
    for j in range(1, ncols):
        for i in range(j):
            Rinv[i][j] = sum(Rinv[i][kk] * R[kk][j] for kk in range(i, j))
        for kk in range(j):
            Rinv[kk][j] = -Rinv[kk][j] / R[j][j]
        Rinv[j][j] = 1 / R[j][j]
    return [[sum(Rinv[i][kk] * Q[j][kk] for kk in range(ncols)) for j in range(nrows)] for i in range(ncols)]


def test_delta_rsi_matches_tbiktag():
    rsi_l, window, degree = 21, 21, 2
    src = ti.rsi(C, rsi_l).to_numpy()
    J = [[math.pow(i, j) for j in range(degree + 1)] for i in range(window)]
    Cm = _mgs_pinv(J, window, degree + 1)
    drsi, err = [], []
    for t in range(N):
        Y = [at(src, t, window - 1 - j) for j in range(window)]
        if any(isna(y) for y in Y):
            drsi.append(NA)
            err.append(NA)
            continue
        a = [sum(Cm[i][j] * Y[j] for j in range(window)) for i in range(degree + 1)]
        d = 0.0
        for i in range(1, degree + 1):
            d = d + i * a[i] * math.pow(window - 1, i - 1)
        Yh = [sum(J[i][j] * a[j] for j in range(degree + 1)) for i in range(window)]
        mse = 0.0
        for i in range(window):
            mse = mse + math.pow(Y[i] - Yh[i], 2) / window
        drsi.append(d)
        err.append(math.sqrt(mse) / (sum(Y) / window))
    r = fm.delta_rsi(C)
    same(r.drsi, drsi, rtol=1e-7, atol=1e-9)
    same(r.nrmse, err, rtol=1e-7, atol=1e-10)
    same(r.signal, ti.ema(pd.Series(drsi, index=C.index), 9), rtol=1e-7, atol=1e-9)


def test_zvwap_matches_lazybear():
    pds = 20
    mean = (V * C).rolling(pds).sum() / V.rolling(pds).sum()
    vwapsd = np.sqrt(ti.sma((C - mean) ** 2, pds))
    same(fm.zvwap(C, V, pds), (C - mean) / vwapsd, rtol=1e-9)


def test_gaussian_stdev_channel_matches_strategy():
    length, mult = 20, 2.0
    half = (length - 1) / 2.0
    denom = (length / 6.0) * (length / 6.0)
    mid, sdv = [], []
    for t in range(N):
        s = nrm = 0.0
        for i in range(length):
            x = i - half
            w = math.exp(-(x * x) / (2 * denom))
            s += at(c, t, i) * w
            nrm += w
        g = s / nrm
        s2 = 0.0
        for i in range(length):
            x = i - half
            w = math.exp(-(x * x) / (2 * denom))
            d = at(c, t, i) - g
            s2 += d * d * w
        mid.append(g)
        sdv.append(math.sqrt(s2 / nrm))
    r = fm.gaussian_stdev_channel(C, length, mult)
    same(r.mid, mid, rtol=1e-12)
    same(r.stdev, sdv, rtol=1e-10)
    same(r.upper, arr(mid) + mult * arr(sdv), rtol=1e-10)


@pytest.mark.parametrize("kind", ["average", "stdev"])
@pytest.mark.parametrize("log_space", [False, True])
def test_babyshark_vw_bands(kind, log_space):
    length = 60
    src = np.log(c) if log_space else c
    basis, dev = [], []
    for t in range(N):
        d_sum = w_sum = 0.0
        for i in range(length):
            d_sum += at(v, t, i) * at(src, t, i)
            w_sum += at(v, t, i)
        b = d_sum / w_sum if not isna(w_sum) else NA
        d_sum = w_sum = 0.0
        for i in range(length):
            cd, cw = at(src, t, i), at(v, t, i)
            d_sum += cw * (math.pow(cd - b, 2) if kind == "stdev" else abs(cd - b))
            w_sum += cw
        basis.append(b)
        dev.append(NA if isna(w_sum) else (math.sqrt(d_sum / w_sum) if kind == "stdev" else d_sum / w_sum))
    b, d = arr(basis), arr(dev)
    r = fm.vw_deviation_bands(C, V, length, kind, log_space)
    f = np.exp if log_space else (lambda x: x)
    same(r.basis, f(b), rtol=1e-12)
    same(r.dev, d, rtol=1e-9)
    same(r.upper2, f(b + d * 2), rtol=1e-12)
    same(r.lower3, f(b - d * 3), rtol=1e-12)


def test_weighted_stdev_from_series_and_arrays():
    n = 20
    out = {k_: [] for k_ in ["m", "v", "d", "mse", "rmse"]}
    sw_s = V.rolling(n).sum().to_numpy()
    sxw = (C * V).rolling(n).sum().to_numpy()
    for t in range(N):
        mean = sxw[t] / sw_s[t] if not isna(sw_s[t]) else NA
        sq = 0.0
        nzn = 0
        for i in range(n):
            sq = sq + math.pow(mean - at(c, t, i), 2) * at(v, t, i)
            nzn = nzn + 1 if at(v, t, i) != 0 and not isna(at(v, t, i)) else nzn
        var = sq / ((nzn - 1) * sw_s[t] / nzn) if nzn > 1 else NA
        out["m"].append(mean)
        out["v"].append(var)
        out["d"].append(math.sqrt(var) if not isna(var) else NA)
        out["mse"].append(sq / sw_s[t] if not isna(sw_s[t]) else NA)
        out["rmse"].append(math.sqrt(sq / sw_s[t]) if not isna(sw_s[t]) else NA)
    r = fm.weighted_stdev(C, V, n)
    for key, got in zip(["m", "v", "d", "mse", "rmse"], r):
        same(got, out[key], rtol=1e-8)

    # arrays version: a_weight = [n, ..., 1] (index 0 = newest close)
    a_w = list(range(n, 0, -1))
    a_src, means, devs = [], [], []
    for t in range(N):
        a_src.insert(0, c[t])
        if len(a_src) > n:
            a_src.pop()
        if len(a_src) >= n:
            sw = sum(a_w)
            mean = sum(a_src[i] * a_w[i] for i in range(n)) / sw
            sq = sum(math.pow(mean - a_src[j], 2) * a_w[j] for j in range(n))
            means.append(mean)
            devs.append(math.sqrt(sq / ((n - 1) * sw / n)))
        else:
            means.append(NA)
            devs.append(NA)
    r = fm.weighted_stdev_linear(C, n)
    same(r.mean, means, rtol=1e-10)
    same(r.mean, ti.wma(C, n), rtol=1e-10)
    same(r.dev, devs, rtol=1e-8)


def test_vpci_dormeier():
    s, lg = 5, 25
    vw = lambda n: (C * V).rolling(n).sum() / V.rolling(n).sum()  # noqa: E731  ta.vwma
    vpc = vw(lg) - ti.sma(C, lg)
    vpr = vw(s) / ti.sma(C, s)
    vm = ti.sma(V, s) / ti.sma(V, lg)
    same(fm.vpci(C, V, s, lg), vpc * vpr * vm, rtol=1e-8)


def _wwma0(x, n):
    out, prev = [], NA
    for val in x:
        y = nz(prev) * (n - 1) / n + val / n if not isna(val) else NA
        out.append(y)
        prev = y
    return out


def test_vawsi_and_hln_match_strategy():
    n = 14
    tr = ti.true_range(H, L, C).to_numpy()  # ta.atr(1)
    aavg = ti.sma(pd.Series(tr), n).to_numpy()
    vavg = ti.sma(V, n).to_numpy()

    def vawma(src):
        out = []
        for t in range(N):
            ws = sw = 0.0
            for i in range(n + 1):
                w = (at(v, t, i) / vavg[t] + at(tr, t, i) / aavg[t]) / 2
                ws += at(src, t, i) * w
                sw += w
            out.append(ws / sw if not isna(sw) else NA)
        return out

    ch = [c[t] - at(c, t, 1) for t in range(N)]
    up = vawma([pmax(x, 0) for x in ch])
    dn = vawma([-pmin(x, 0) if not isna(x) else NA for x in ch])
    rsi = [100 - (100 / (1 + div(a, b))) if not isna(div(a, b)) else NA for a, b in zip(up, dn)]
    same(fm.vawsi(C, H, L, C, V, n), rsi, rtol=1e-10)

    TR = [pmax(abs(c[t] - at(c, t, 1)) if t else NA, h[t] - l[t]) for t in range(N)]
    rm = _wwma0(TR, n)
    hln = []
    for t in range(N):
        ch_rm = rm[t] - at(rm, t, 1)
        x = div(c[t], abs(ch_rm)) if not isna(ch_rm) else NA
        hln.append(div(1, x) * 100 if not isna(div(1, x)) else NA)
    same(fm.vawsi_hln(C, H, L, n), hln, rtol=1e-9)


@pytest.mark.parametrize("trail_type", ["modified", "unmodified"])
def test_blackflag_fts_matches_duyck_source(trail_type):
    P, F = 28, 5.0
    hl_sma = ti.sma(H - L, P).to_numpy()
    trail, trend, ex_o = [], [], []
    wild = NA
    TU = TD = TRD = EX = NA
    for t in range(N):
        h1, l1, c1 = at(h, t, 1), at(l, t, 1), at(c, t, 1)
        HiLo = pmin(h[t] - l[t], 1.5 * nz(hl_sma[t]))
        HRef = h[t] - c1 if (not isna(h1) and l[t] <= h1) else (h[t] - c1) - 0.5 * (l[t] - h1)
        LRef = c1 - l[t] if (not isna(l1) and h[t] >= l1) else (c1 - l[t]) - 0.5 * (l1 - h[t])
        if trail_type == "modified":
            trueRange = pmax(HiLo, HRef, LRef)
        else:
            trueRange = pmax(h[t] - l[t], abs(h[t] - c1), abs(l[t] - c1))
        wild = nz(wild) + (trueRange - nz(wild)) / P
        loss = F * wild
        Up, Dn = c[t] - loss, c[t] + loss
        tu = pmax(Up, TU) if gt(c1, TU) else Up
        td = pmin(Dn, TD) if lt(c1, TD) else Dn
        trd = 1 if gt(c[t], TD) else (-1 if lt(c[t], TU) else nz(TRD, 1))
        if trd > 0 and not isna(TRD) and TRD <= 0:
            ex = h[t]
        elif trd < 0 and not isna(TRD) and TRD >= 0:
            ex = l[t]
        elif trd == 1:
            ex = pmax(EX, h[t])
        elif trd == -1:
            ex = pmin(EX, l[t])
        else:
            ex = EX
        trail.append(tu if trd == 1 else td)
        trend.append(trd)
        ex_o.append(ex)
        TU, TD, TRD, EX = tu, td, trd, ex
    r = fm.blackflag_fts(H, L, C, trail_type)
    same(r.trail, trail, rtol=1e-12)
    same(r.trend, trend)
    same(r.extremum, ex_o)
    e, tr_ = arr(ex_o), arr(trail)
    same(r.fib2, e + (tr_ - e) * 78.6 / 100, rtol=1e-12)
    assert (r.trend == -1).sum() > 100 and (r.trend == 1).sum() > 100


def test_range_volatility_matches_wbburgin():
    vl, m = 100, 100
    hh, ll = C.rolling(vl).max().to_numpy(), C.rolling(vl).min().to_numpy()
    vx = 2 * (hh - ll) / (hh + ll)
    hb = c + c * vx
    up = []
    for t in range(N):
        norm = s = 0.0
        for i in range(m):
            norm += vx[t]
            s += at(hb, t, i) * vx[t]
        up.append(div(s, norm))
    r = fm.range_volatility(C, vl, m)
    same(r.volatility, vx, rtol=1e-12)
    same(r.upper, up, rtol=1e-9)


def test_volume_strength_finder():
    sess = pd.Series(ti.session_ids(C.index, "D"), index=C.index)
    s = sess.to_numpy()
    sp_o, sn_o = [], []
    for t in range(N):
        z1 = t
        while z1 > 0 and s[z1 - 1] == s[t]:
            z1 -= 1
        L_ = t - z1 + 1
        SSPV = SSNV = 0.0
        for i in range(1, L_):  # 1 .. L-1 (empty on the session's first bar)
            total_w = at(h, t, i) - at(l, t, i)
            pdw = div(at(c, t, i) - at(l, t, i), total_w)
            ndw = div(at(h, t, i) - at(c, t, i), total_w)
            pdw = pdw * 100 if not isna(pdw) else NA
            ndw = ndw * 100 if not isna(ndw) else NA
            SSPV = at(v, t, i) * pdw / 100 + SSPV if not (isna(pdw) or isna(SSPV)) else NA
            SSNV = at(v, t, i) * ndw / 100 + SSNV if not (isna(ndw) or isna(SSNV)) else NA
        sp_o.append(SSPV)
        sn_o.append(SSNV)
    r = fm.volume_strength(H, L, C, V, sess)
    same(r.sspv, sp_o, rtol=1e-10)
    same(r.ssnv, sn_o, rtol=1e-10)
    tot = arr(sp_o) + arr(sn_o)
    with np.errstate(invalid="ignore", divide="ignore"):
        pos = np.where(tot == 0, np.nan, arr(sp_o) / tot * 100)
    same(r.pos, pos, rtol=1e-10)


@pytest.mark.parametrize("start", [0, 1])
def test_tmo(start):
    length, cl, sl = 45, 12, 9  # the 15MIN BTCUSDTPERP BOT inputs
    data = []
    for t in range(N):
        d = 0
        for i in range(start, length):  # Mobius: fold i = 0 to length; copy: for i = 1 to tmolength-1
            if gt(c[t], at(o, t, i)):
                d += 1
            if lt(c[t], at(o, t, i)):
                d -= 1
        data.append(float(d))
    ds = pd.Series(data, index=C.index)
    main = ti.ema(ti.ema(ds, cl), sl)
    r = fm.tmo(O, C, length, cl, sl, start)
    same(r.raw, data)
    same(r.main, main, rtol=1e-10)
    same(r.signal, ti.ema(main, sl), rtol=1e-10)


def test_for_loop_score_on_zero_lag_basis():
    length = 50
    lag = math.floor((length - 1) / 2)
    basis = ti.ema(2 * C - C.shift(lag), length).to_numpy()
    out = []
    for t in range(N):
        s = 0
        for i in range(1, 51):
            if gt(basis[t], at(basis, t, i)):
                s += 1
            elif lt(basis[t], at(basis, t, i)):
                s -= 1
        out.append(float(s))
    same(fm.for_loop_score(basis, 1, 50), out)


def test_price_friction_lube():
    bb, rng = 500, 100
    fr = []
    for t in range(N):
        f = 0.0
        for i in range(1, bb + 1):
            f = f + (1 + bb) / (i + bb) if (gt(at(h, t, i), c[t]) or at(h, t, i) == c[t]) and (lt(at(l, t, i), c[t]) or at(l, t, i) == c[t]) else f
        fr.append(f)
    fs = pd.Series(fr, index=C.index)
    lo, hi = fs.rolling(rng).min(), fs.rolling(rng).max()
    r = fm.price_friction(H, L, C, bb, rng, 50, -10)
    same(r.friction, fr, rtol=1e-12)
    same(r.mid_f, lo * 0.5 + hi * 0.5, rtol=1e-12)
    same(r.trigger, lo * 1.1 + hi * -0.1, rtol=1e-12, atol=1e-9)


@pytest.mark.parametrize("smoothing", [1, 7])
def test_rsi_heikin_ashi_matches_jayrogers(smoothing):
    n = 14
    cr = (ti.rsi(C, n) - 50).to_numpy()
    hr = (ti.rsi(H, n) - 50).to_numpy()
    lr = (ti.rsi(L, n) - 50).to_numpy()
    O_, H_, L_, C_ = [], [], [], []
    for t in range(N):
        _openRSI = nz(at(cr, t, 1), cr[t])
        _highRSI = pmax(hr[t], lr[t])
        _lowRSI = pmin(hr[t], lr[t])
        _close = (_openRSI + _highRSI + _lowRSI + cr[t]) / 4
        if isna(at(O_, t, smoothing)):
            _open = (_openRSI + cr[t]) / 2
        else:
            _open = ((O_[t - 1] * smoothing) + C_[t - 1]) / (smoothing + 1)
        O_.append(_open)
        C_.append(_close)
        H_.append(pmax(_highRSI, pmax(_open, _close)))
        L_.append(pmin(_lowRSI, pmin(_open, _close)))
    r = fm.rsi_heikin_ashi(H, L, C, n, smoothing)
    same(r.open, O_, rtol=1e-10)
    same(r.high, H_, rtol=1e-10)
    same(r.low, L_, rtol=1e-10)
    same(r.close, C_, rtol=1e-10)


@pytest.mark.parametrize("binary", [False, True])
def test_relative_body_index(binary):
    t_ = 5
    s = pd.Series([(1.0 if c[t] > o[t] else -1.0) if binary else div(c[t] - o[t], h[t] - l[t]) for t in range(N)],
                  index=C.index)
    yn = ti.ema(s.rolling(t_).sum(), t_)
    r = fm.relative_body_index(O, H, L, C, t_, 5, binary)
    same(r.rbi, yn, rtol=1e-10)
    same(r.signal, ti.ema(yn, 5), rtol=1e-10)


def test_hurst_rescaled_range():
    n = 50
    ret = np.log(c[1:] / c[:-1])
    out = [NA] * N
    for t in range(n, N):
        x = ret[t - n:t]  # the n log returns ending at bar t
        y = np.cumsum(x - x.mean())
        rr = max(y.max(), 0.0) - min(y.min(), 0.0)
        out[t] = math.log(rr / x.std()) / math.log(n)
    got = fm.hurst_exponent(C, n)
    same(got, out, rtol=1e-9)
    # a strongly trending series scores higher than a mean-reverting one
    trend = pd.Series(np.exp(np.cumsum(np.full(400, 0.01) + np.sin(np.arange(400)) * 0.002)))
    revert = pd.Series(100 + np.sin(np.arange(400) * 2.5))
    assert fm.hurst_exponent(trend, n).iloc[-1] > fm.hurst_exponent(revert, n).iloc[-1]


@pytest.mark.parametrize("below_zero", [True, False])
def test_weis_wave_volume_matches_lazybear(below_zero):
    tdl = 4  # the strategy's trendDetectionLength
    trend = wave = vol = mov1 = NA
    W, VO, UP, DN = [], [], [], []
    for t in range(N):
        mov = 1 if gt(c[t], at(c, t, 1)) else (-1 if lt(c[t], at(c, t, 1)) else 0)
        trend = mov if (mov != 0 and not isna(mov1) and mov != mov1) else nz(trend)
        rising = all(gt(c[t], at(c, t, i)) for i in range(1, tdl + 1))
        falling = all(lt(c[t], at(c, t, i)) for i in range(1, tdl + 1))
        new_wave = trend if (trend != nz(wave) and (rising or falling)) else nz(wave)
        vol = nz(vol) + v[t] if (not isna(wave) and new_wave == wave) else v[t]
        wave = new_wave
        mov1 = mov
        W.append(wave)
        VO.append(vol)
        UP.append(vol if wave == 1 else 0.0)
        if below_zero:
            DN.append(0.0 if wave == 1 else (-vol if wave == -1 else vol))
        else:
            DN.append(0.0 if wave == 1 else vol)
    r = fm.weis_wave_volume(C, V, tdl, below_zero)
    same(r.wave, W)
    same(r.wave_volume, VO, rtol=1e-12)
    same(r.up, UP, rtol=1e-12)
    same(r.down, DN, rtol=1e-12)


def test_faytterro_estimator():
    n = 10
    src = ((H + L + C) / 3).to_numpy()
    y = 2 * n - 1
    cr = []
    for t in range(N):
        z = 0.0
        for i in range(y):
            z = z + at(src, t, i) * ((y - 1) / 2 + 1 - abs(i - (y - 1) / 2))
        cr.append(z / (((y + 1) / 2) * (y + 1) / 2))
    buy, sell, fc = [], [], []
    for t in range(N):
        a, b, cc = cr[t], at(cr, t, 1), at(cr, t, 2)
        dizi = [i * (i - 1) * (a - 2 * b + cc) / 2 + i * (b - cc) + cc for i in range(2 * n + 1)]
        d6, d5 = dizi[n + 1 + 5], dizi[n + 1 + 4]
        buy.append(gt(d6, d5) and lt(d6, at(cr, t, n)))
        sell.append(lt(d6, d5) and gt(d6, at(cr, t, n)))
        fc.append(d6)
    r = fm.faytterro_estimator(pd.Series(src, index=C.index), n)
    same(r.estimator, cr, rtol=1e-12)
    same(r.estimator, ti.trima(pd.Series(src), 2 * n - 1), rtol=1e-10)
    same(r.forecast, fc, rtol=1e-8)
    assert (r.buy.to_numpy() == np.array(buy)).all() and (r.sell.to_numpy() == np.array(sell)).all()
    assert sum(buy) > 10 and sum(sell) > 10


def test_gyroscopic_bands_matches_jomy():
    vara, varb = 10 ** 4.0, 12
    a = 0
    pos_l, traj_l = [], []
    pos1 = traj1 = NA
    for t in range(N):
        a = nz(a) + 1 if v[t] > -1 else 0
        pos = c[t] if a <= 5 else nz(pos1)
        grav = 1 / math.sqrt((c[t] * c[t])) * vara
        traj = (nz(at(c, t, 1)) - nz(at(c, t, 2)) + nz(traj1) * varb) / (varb + 1)
        pos = nz(pos1) + grav + traj if pos < c[t] else nz(pos1) - grav + traj
        pos_l.append(pos)
        traj_l.append(traj)
        pos1, traj1 = pos, traj
    r = fm.gyroscopic_bands(C, 4.0, varb)
    same(r.pos, pos_l, rtol=1e-9, atol=1e-6)
    same(r.traj, traj_l, rtol=1e-9, atol=1e-9)
    dist = ti.sma((C - pd.Series(pos_l, index=C.index)).abs(), varb)
    same(r.upper, arr(pos_l) + dist, rtol=1e-9, atol=1e-6)


def _profile_ref(hs, ls, vs, rows, va):
    """Plain-Python rolling profile: uniform spread over each bar's range,
    TradingView's value-area expansion."""
    hi, lo = max(hs), min(ls)
    if hi <= lo:
        return hi, hi, hi
    step = (hi - lo) / rows
    hist = [0.0] * rows
    for hj, lj, vj in zip(hs, ls, vs):
        if hj <= lj:
            hist[min(int((hj - lo) / step), rows - 1)] += vj
            continue
        for r in range(rows):
            bot = lo + r * step
            top = hi if r == rows - 1 else bot + step
            ov = min(hj, top) - max(lj, bot)
            if ov > 0:
                hist[r] += vj * ov / (hj - lj)
    p = max(range(rows), key=lambda r: (hist[r], -r))
    target = sum(hist) * va / 100
    vol = hist[p]
    up, dn = p + 1, p - 1
    while up < rows or dn >= 0:
        cand = []
        if up < rows:
            cand.append((hist[up], -(up - p), 1, up))
        if dn >= 0:
            cand.append((hist[dn], -(p - dn), 0, dn))
        best = max(cand)
        if vol + best[0] > target + 1e-12 * target:
            break
        vol += best[0]
        if best[2]:
            up += 1
        else:
            dn -= 1
    return lo + (p + 0.5) * step, lo + up * step, lo + (dn + 1) * step


def test_volume_profile_rolling_poc_vah_val():
    n, rows, va = 100, 24, 70.0
    r = fm.volume_profile(H, L, V, n, rows, va)
    assert r.poc.iloc[: n - 1].isna().all() and r.poc.iloc[n - 1:].notna().all()
    for t in range(N - 400, N):
        ref = _profile_ref(h[t - n + 1:t + 1], l[t - n + 1:t + 1], v[t - n + 1:t + 1], rows, va)
        np.testing.assert_allclose([r.poc.iloc[t], r.vah.iloc[t], r.val.iloc[t]], ref, rtol=1e-12)
    ok = r.poc.notna()
    assert (r.vah[ok] >= r.poc[ok]).all() and (r.val[ok] <= r.poc[ok]).all()
    # no look-ahead: changing the future does not change the past
    h2, l2, v2 = H.copy(), L.copy(), V.copy()
    v2.iloc[2000:] *= 50
    h2.iloc[2000:] *= 1.5
    r2 = fm.volume_profile(h2, l2, v2, n, rows, va)
    same(r2.poc.iloc[:2000], r.poc.iloc[:2000])
    same(r2.vah.iloc[:2000], r.vah.iloc[:2000])


def test_volume_profile_value_area_by_hand():
    # three bars: 100 volume in the low row, 300 in the middle, 50 at the top
    hh = pd.Series([1.0, 2.0, 3.0])
    ll = pd.Series([0.0, 1.0, 2.0])
    vv = pd.Series([100.0, 300.0, 50.0])
    r = fm.volume_profile(hh, ll, vv, length=3, rows=3, value_area=70)
    assert r.poc.iloc[-1] == 1.5
    # 70 % of 450 = 315: POC row (300) fits, the next larger neighbour (100) would exceed it
    assert r.vah.iloc[-1] == 2.0 and r.val.iloc[-1] == 1.0
    r = fm.volume_profile(hh, ll, vv, length=3, rows=3, value_area=95)
    assert r.vah.iloc[-1] == 2.0 and r.val.iloc[-1] == 0.0  # 400 <= 427.5, adding 50 exceeds it


def test_volume_heatmap_matches_strategy():
    lb, lv, pct = 100, 10, 0.01
    B, S = [], []
    for t in range(N):
        cb = cs = 0.0
        for i in range(lv):
            level = c[t] * (1 + (i - lv / 2) * pct)
            buyVol = sellVol = 0.0
            for j in range(1, lb + 1):
                cj, oj = at(c, t, j), at(o, t, j)
                if gt(cj, oj):
                    if (gt(cj, level) or cj == level) and (lt(at(l, t, j), level) or at(l, t, j) == level):
                        buyVol = buyVol + at(v, t, j)
                else:
                    if (lt(cj, level) or cj == level) and (gt(at(h, t, j), level) or at(h, t, j) == level):
                        sellVol = sellVol + at(v, t, j)
            cb += buyVol
            cs += sellVol
        B.append(cb)
        S.append(cs)
    r = fm.volume_heatmap(O, H, L, C, V, lb, lv, pct)
    same(r.buy, B, rtol=1e-12)
    same(r.sell, S, rtol=1e-12)


def test_registry_and_frames():
    assert set(fm.EXTRA_MISC) and not (set(fm.EXTRA_MISC) & set(ti._core.REGISTRY))
    df = pd.DataFrame({"a": c, "b": c[::-1].copy()}, index=C.index)
    r = fm.nadaraya_watson_rq(df)
    same(r.yhat1["b"], fm.nadaraya_watson_rq(df["b"]).yhat1)
    r = fm.volume_rsi(df, V)
    assert r.shape == df.shape
