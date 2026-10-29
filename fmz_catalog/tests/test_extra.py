"""Tests for the staging indicators in fmz_catalog/extra.py.

TA-Lib where it has the indicator; otherwise a literal bar-by-bar port of the
source script (FMZ's open-source TA.KDJ, BeikabuOyaji's ADX and DI,
everget's JMA, DonovanWall's Gaussian filter, HPotter's 123 Reversal...).
"""

import math

import numpy as np
import pandas as pd
import pytest

import fmz_catalog.extra as fx
from tv_indicators.tests.test_indicators import TAIL, C, H, L, N, c, h, l, same

talib = pytest.importorskip("talib")


def nz(x):
    return 0.0 if x is None or (isinstance(x, float) and math.isnan(x)) else x


def test_tsf_matches_talib():
    same(fx.tsf(C, 14), talib.TSF(c, 14), rtol=1e-8)


def test_mama_converges_to_talib():
    m, f = talib.MAMA(c, 0.5, 0.05)
    r = fx.mama(C)
    same(r.mama, m, tail=TAIL, rtol=1e-6)
    same(r.fama, f, tail=TAIL, rtol=1e-6)


def test_kdj_matches_fmz_ta_kdj():
    n, kk, dd = 9, 3, 3
    K, D = [], []
    kp = dp = 50.0
    for i in range(N):
        if i >= n - 1:
            hh, ll = h[i - n + 1:i + 1].max(), l[i - n + 1:i + 1].min()
            rsv = 100 * (c[i] - ll) / (hh - ll) if hh != ll else 50.0
            kp = (rsv + (kk - 1) * kp) / kk
            dp = (kp + (dd - 1) * dp) / dd
            K.append(kp)
            D.append(dp)
        else:
            K.append(np.nan)
            D.append(np.nan)
    r = fx.kdj(H, L, C)
    same(r.k, K)
    same(r.d, D)
    same(r.j, 3 * np.array(K) - 2 * np.array(D))


def test_sma_cn_and_rma_relation():
    s = fx.sma_cn(C, 14, 1).to_numpy()
    y, out = None, []
    for v in c:
        y = v if y is None else (v + 13 * y) / 14
        out.append(y)
    same(s, out)


def test_dma_cn():
    a = pd.Series(np.where(np.arange(N) % 7 == 0, 1.5, 0.2), index=C.index)  # invalid alpha every 7th bar
    out, y = [], np.nan
    for v, al in zip(c, a):
        if 0 < al < 1:
            y = v if np.isnan(y) else al * v + (1 - al) * y
        out.append(y)
    same(fx.dma_cn(C, a), out)


def test_hv_lv_and_sample_std():
    r = fx.hv_lv(H, L, 20)
    same(r.hv, H.rolling(20).max().shift(1))
    same(r.lv, L.rolling(20).min().shift(1))
    same(fx.stdev_sample(C, 20), C.rolling(20).std(), rtol=1e-8)


def test_wwma_and_zlema_half_lag():
    out, y = [], 0.0
    for v in c:
        y = v / 14 + (1 - 1 / 14) * y
        out.append(y)
    same(fx.wwma(C, 14), out)
    same(fx.zlema_half_lag(C, 20), talib.EMA((2 * C - C.shift(10)).to_numpy(), 20))


def test_ssf_ports():
    arg = math.sqrt(2) * math.pi / 10
    a1 = math.exp(-arg)
    c2, c3 = 2 * a1 * math.cos(arg), -a1 * a1
    c1 = 1 - c2 - c3
    s1 = s2 = 0.0
    out = []
    for v in c:
        y = c1 * v + c2 * s1 + c3 * s2
        s2, s1 = s1, y
        out.append(y)
    same(fx.ssf2(C, 10), out)


def test_gaussian_matches_donovanwall_weights():
    per, n = 144, 4
    beta = (1 - math.cos(2 * math.pi / per)) / (math.pow(1.414, 2 / n) - 1)
    al = -beta + math.sqrt(beta * beta + 2 * beta)
    x = 1 - al
    f = [0.0] * 4
    out = []
    for v in c:
        y = al ** 4 * v + 4 * x * f[0] - 6 * x ** 2 * f[1] + 4 * x ** 3 * f[2] - x ** 4 * f[3]
        f = [y] + f[:3]
        out.append(y)
    hlc3 = (H + L + C) / 3
    f = [0.0] * 4
    ch = []
    for v in hlc3.to_numpy():
        y = al ** 4 * v + 4 * x * f[0] - 6 * x ** 2 * f[1] + 4 * x ** 3 * f[2] - x ** 4 * f[3]
        f = [y] + f[:3]
        ch.append(y)
    same(fx.gaussian_channel(H, L, C, per, n).filter, ch)  # script's 1.414 for sqrt(2)
    same(fx.gaussian_filter(C, per, n), out, rtol=1e-3)  # Ehlers' exact sqrt(2): warm-up only


def test_jma_everget_port():
    length, phase, power = 7, 50, 2
    pr = phase / 100 + 1.5
    beta = 0.45 * (length - 1) / (0.45 * (length - 1) + 2)
    alpha = beta ** power
    e0 = e1 = e2 = j = 0.0
    out = []
    for s in c:
        e0 = (1 - alpha) * s + alpha * e0
        e1 = (s - e0) * (1 - beta) + beta * e1
        e2 = (e0 + pr * e1 - j) * (1 - alpha) ** 2 + alpha ** 2 * e2
        j = e2 + j
        out.append(j)
    same(fx.jma(C), out)


def test_adx_sma_beikabuoyaji_port():
    n = 14
    s_tr = s_p = s_m = 0.0
    dip, dim, dx = [], [], []
    for i in range(N):
        pc = c[i - 1] if i else 0.0
        ph = h[i - 1] if i else 0.0
        pl = l[i - 1] if i else 0.0
        tr = max(max(h[i] - l[i], abs(h[i] - pc)), abs(l[i] - pc))
        dmp = max(h[i] - ph, 0) if h[i] - ph > pl - l[i] else 0
        dmm = max(pl - l[i], 0) if pl - l[i] > h[i] - ph else 0
        s_tr = s_tr - s_tr / n + tr
        s_p = s_p - s_p / n + dmp
        s_m = s_m - s_m / n + dmm
        p, m = s_p / s_tr * 100, s_m / s_tr * 100
        dip.append(p)
        dim.append(m)
        dx.append(abs(p - m) / (p + m) * 100)
    r = fx.adx_sma(H, L, C)
    same(r.plus_di, dip)
    same(r.adx, pd.Series(dx).rolling(n).mean())
    # The DI lines converge to TradingView's; ADX keeps its SMA-vs-RMA gap.
    import tv_indicators as ti
    tv = ti.dmi(H, L, C)
    same(r.plus_di, tv.plus_di, tail=TAIL, rtol=1e-6)
    assert np.nanmax(np.abs(r.adx.to_numpy()[-TAIL:] - tv.adx.to_numpy()[-TAIL:])) > 1.0


def test_reversal_123_port():
    st = 100 * (C - L.rolling(14).min()) / (H.rolling(14).max() - L.rolling(14).min())
    fast = st.rolling(1).mean().to_numpy()
    slow = pd.Series(fast).rolling(3).mean().to_numpy()
    pos, out = 0.0, []
    for i in range(N):
        if i >= 2:
            if c[i - 2] < c[i - 1] and c[i] > c[i - 1] and fast[i] < slow[i] and fast[i] > 50:
                pos = 1.0
            elif c[i - 2] > c[i - 1] and c[i] < c[i - 1] and fast[i] > slow[i] and fast[i] < 50:
                pos = -1.0
        out.append(pos)
    same(fx.reversal_123(H, L, C).pos, out)


def test_helpers():
    r = fx.rising_falling(C, 3)
    exp = (C > C.shift(1)) & (C > C.shift(2)) & (C > C.shift(3))
    np.testing.assert_array_equal(r.rising.to_numpy(), exp.to_numpy())
    cond = C > C.rolling(20).mean()
    vw = fx.valuewhen(cond, C, 1).to_numpy()
    s = C.where(cond)
    exp_vw = s.dropna().shift(1).reindex(C.index).ffill().to_numpy()
    same(vw, exp_vw)
    p = fx.percentile(C, 20, 30.0, "linear")
    same(p, C.rolling(20).quantile(0.3, interpolation="linear"))
    fvg = fx.fair_value_gap(H, L)
    np.testing.assert_array_equal(fvg.bull.to_numpy(), (L > H.shift(2)).to_numpy())


def test_kept_out_of_main_registry():
    import tv_indicators as ti

    assert "KDJ" not in ti.REGISTRY and "KDJ" in fx.EXTRA
