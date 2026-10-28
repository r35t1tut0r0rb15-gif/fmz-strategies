"""Tests for the second batch of indicators.

TA-Lib where it has the same formula, otherwise an independent pandas/scipy
re-computation of the documented formula. The community scripts and TV
built-ins of this batch are also ported bar by bar from their Pine source in
test_pine_ports_*.py.
"""

import numpy as np
import pandas as pd
import pytest

import tv_indicators as ti
from tv_indicators.tests.test_indicators import TAIL, C, D, H, L, N, O, V, c, h, l, o, same, v

talib = pytest.importorskip("talib")
stats = pytest.importorskip("scipy.stats")

BENCH = pd.Series(100 * np.exp(np.cumsum(np.random.default_rng(3).normal(0, 0.008, N))), index=D.index)
B = BENCH.to_numpy()


# --- TA-Lib -----------------------------------------------------------------

@pytest.mark.parametrize("n", [5, 20, 21])
def test_trima_mid(n):
    same(ti.trima(C, n), talib.TRIMA(c, n))
    same(ti.midpoint(C, n), talib.MIDPOINT(c, n))
    same(ti.midprice(H, L, n), talib.MIDPRICE(h, l, n))


def test_t3():
    same(ti.t3(C, 5, 0.7), talib.T3(c, 5, 0.7), tail=TAIL)


def test_stats_talib():
    same(ti.stdev(C, 20), talib.STDDEV(c, 20, 1))
    same(ti.variance(C, 20), talib.VAR(c, 20, 1), rtol=1e-7)
    same(ti.correlation(C, BENCH, 20), talib.CORREL(c, B, 20), rtol=1e-6, atol=1e-8)
    lr = ti.linreg(C, 14)
    same(lr.value, talib.LINEARREG(c, 14))
    same(lr.slope, talib.LINEARREG_SLOPE(c, 14), atol=1e-8)
    same(lr.intercept, talib.LINEARREG_INTERCEPT(c, 14), rtol=1e-8)
    same(lr.angle, talib.LINEARREG_ANGLE(c, 14), atol=1e-6)
    same(ti.beta(C, BENCH, 20), talib.BETA(B, c, 20), rtol=1e-6, atol=1e-8)


def test_ppo_apo_adxr_bop():
    same(ti.ppo(C).ppo, talib.PPO(c, 12, 26, 1), tail=TAIL)
    same(ti.apo(C, ma_type="sma"), talib.APO(c, 12, 26, 0))
    same(ti.adxr(H, L, C), talib.ADXR(h, l, c, 14), tail=TAIL, rtol=1e-7)
    ours = ti.bop(O, H, L, C).to_numpy()
    tl = talib.BOP(o, h, l, c)
    m = h != l
    same(ours[m], tl[m])
    assert np.isnan(ours[~m]).all()


# --- independent re-computations --------------------------------------------

def test_simple_mas():
    n = 20
    lag = (n - 1) // 2
    same(ti.zlema(C, n), talib.EMA((2 * C - C.shift(lag)).to_numpy(), n))
    same(ti.swma(C), C.rolling(4).apply(lambda x: np.dot(x, [1, 2, 2, 1]) / 6, raw=True))
    same(ti.ehma(C, 55), talib.EMA(2 * talib.EMA(c, 27) - talib.EMA(c, 55), 7))
    inner = 3 * talib.WMA(c, 18) - talib.WMA(c, 27) - talib.WMA(c, 55)
    same(ti.thma(C, 55), talib.WMA(inner, 55))
    same(ti.median(C, 5), C.rolling(5).median())
    same(ti.median(C, 4), C.rolling(4).median())
    g = ti.gmma(C)
    same(g.ema60, talib.EMA(c, 60))
    l1 = talib.LINEARREG(c, 32)
    same(ti.zlsma(C), 2 * l1 - talib.LINEARREG(l1, 32))
    m = c
    for n_ in (3, 5, 8, 13, 21, 34):
        m = talib.WMA(m, n_)
    same(ti.mavilimw(C), m)


def test_filters_recursions():
    # super smoother, ultimate smoother, laguerre: direct loops
    n = 10
    a1 = np.exp(-1.414 * np.pi / n)
    c2 = 2 * a1 * np.cos(1.414 * np.pi / n)
    c3 = -a1 * a1
    c1 = 1 - c2 - c3
    ss = []
    for i in range(N):
        p1 = c[i - 1] if i else 0.0
        s1 = ss[i - 1] if i > 0 else 0.0
        s2 = ss[i - 2] if i > 1 else 0.0
        ss.append(c1 * (c[i] + p1) / 2 + c2 * s1 + c3 * s2)
    same(ti.supersmoother(C, n), ss)

    g = 0.8
    l0 = l1 = l2 = l3 = 0.0
    out = []
    for i in range(N):
        n0 = (1 - g) * c[i] + g * l0
        n1 = -g * n0 + l0 + g * l1
        n2 = -g * n1 + l1 + g * l2
        n3 = -g * n2 + l2 + g * l3
        l0, l1, l2, l3 = n0, n1, n2, n3
        out.append((l0 + 2 * l1 + 2 * l2 + l3) / 6)
    same(ti.laguerre(C, g), out)


def test_vidya_matches_definition():
    n, alpha = 9, 2 / 10
    d = C.diff()
    ud = d.clip(lower=0).fillna(0).rolling(9).sum()
    dd = (-d).clip(lower=0).fillna(0).rolling(9).sum()
    cmo = ((ud - dd) / (ud + dd)).fillna(0).to_numpy()
    var, out = 0.0, []
    for i in range(N):
        kk = alpha * abs(cmo[i])
        var = kk * c[i] + (1 - kk) * var
        out.append(var)
    same(ti.vidya(C, n), out)


def test_frama_and_cog_basic():
    f = ti.frama(H, L, 16).to_numpy()
    hl2 = (h + l) / 2
    assert np.isfinite(f).all()
    assert np.nanmax(np.abs(f[100:] - hl2[100:]) / hl2[100:]) < 0.2
    cg = ti.center_of_gravity(H, L, 10).cg
    w = np.arange(1, 11)
    exp = pd.Series(hl2).rolling(10).apply(lambda x: -np.dot(x[::-1], w) / x.sum() + 5.5, raw=True)
    same(cg, exp)


def test_nadaraya_watson_endpoint():
    r = ti.nadaraya_watson(C, 8.0, 3.0, 500)
    w = np.exp(-(np.arange(500) ** 2) / (2 * 64.0))
    exp = C.rolling(500).apply(lambda x: np.dot(x[::-1], w) / w.sum(), raw=True)
    same(r.estimate, exp)
    same(r.upper - r.estimate, (C - exp).abs().rolling(499).mean() * 3)


def test_oscillator_formulas():
    same(ti.zscore(C, 20), (C - C.rolling(20).mean()) / C.rolling(20).std(ddof=0))
    e = talib.EMA(c, 13)
    bb = ti.bull_bear_power(H, L, C)
    same(bb.bull, h - e)
    dh = H.diff()
    dl = -L.diff()
    dmax = dh.where(dh > 0, 0).where(dh.notna()).rolling(14).mean()
    dmin = dl.where(dl > 0, 0).where(dl.notna()).rolling(14).mean()
    same(ti.demarker(H, L), dmax / (dmax + dmin))
    up = (C.diff() > 0).astype(float).where(C.diff().notna())
    same(ti.psychological_line(C), up.rolling(12).sum() / 12 * 100)
    sm = C.rolling(14).mean()
    same(ti.disparity_index(C), (C - sm) / sm * 100)
    same(ti.efficiency_ratio(C, 10), C.diff(10).abs() / C.diff().abs().rolling(10).sum())
    same(ti.vhf(C, 28), (C.rolling(28).max() - C.rolling(28).min()) / C.diff().abs().rolling(28).sum())
    same(ti.chande_forecast_oscillator(C), (c - talib.LINEARREG(c, 14)) / c * 100)
    tr = ti.true_range(H, L, C).to_numpy()
    same(ti.pretty_good_oscillator(H, L, C), (c - talib.SMA(c, 14)) / talib.EMA(tr, 14))
    d = C - O
    g, ls = d.clip(lower=0).rolling(14).sum(), (-d).clip(lower=0).rolling(14).sum()
    same(ti.intraday_momentum_index(O, C), g / (g + ls) * 100)
    atr = ti.atr(H, L, C, 14)
    same(ti.random_walk_index(H, L, C).rwi_high, (H - L.shift(14)) / (atr * np.sqrt(14)))
    atr26 = ti.atr(H, L, C, 26).to_numpy()
    same(ti.macd_v(H, L, C).macd_v, (talib.EMA(c, 12) - talib.EMA(c, 26)) / atr26 * 100)
    same(ti.elliott_wave_oscillator(C), talib.SMA(c, 5) - talib.SMA(c, 35))
    same(ti.qstick(O, C), (C - O).rolling(8).mean())
    rsi = talib.RSI(c, 13)
    t = ti.tdi(C)
    same(t.price_line, talib.SMA(rsi, 2))
    same(t.upper, talib.SMA(rsi, 34) + 1.6185 * talib.STDDEV(rsi, 34, 1))
    v1 = talib.WMA(0.1 * (talib.RSI(c, 5) - 50), 9)
    same(ti.inverse_fisher_rsi(C), np.tanh(v1), atol=1e-12)
    e1 = talib.EMA(h - l, 10)
    same(ti.chaikin_volatility(H, L), (e1 - np.r_[np.full(10, np.nan), e1[:-10]]) / np.r_[np.full(10, np.nan), e1[:-10]] * 100)
    hh = C.rolling(14).max()
    same(ti.ulcer_index(C), np.sqrt((((C - hh) / hh * 100) ** 2).rolling(14).mean()))


def test_rmi_is_rsi_on_momentum():
    # RMI with momentum 1 is RSI
    same(ti.rmi(C, 14, 1), talib.RSI(c, 14))


def test_trend_strength_and_rci():
    t = np.arange(N, dtype=float)
    exp = pd.Series(c).rolling(14).corr(pd.Series(t))
    same(ti.trend_strength_index(C, 14), exp, rtol=1e-6, atol=1e-8)
    exp_rci = pd.Series(c).rolling(9).apply(lambda x: 100 * stats.spearmanr(np.arange(9), x)[0], raw=True)
    same(ti.rci(C, 9), exp_rci, rtol=1e-7, atol=1e-8)


def test_linreg_r2():
    r2 = ti.linreg(C, 14).r2.to_numpy()
    i = 500
    res = stats.linregress(np.arange(14), c[i - 13:i + 1])
    assert abs(r2[i] - res.rvalue ** 2) < 1e-9


def test_volatility_estimators():
    n = 20
    hl = np.log(H / L)
    same(ti.parkinson(H, L, n), np.sqrt((hl ** 2).rolling(n).mean() / (4 * np.log(2))))
    co = np.log(C / O)
    same(ti.garman_klass(O, H, L, C, n), np.sqrt((0.5 * hl ** 2 - (2 * np.log(2) - 1) * co ** 2).rolling(n).mean()))
    rs = np.log(H / C) * np.log(H / O) + np.log(L / C) * np.log(L / O)
    same(ti.rogers_satchell(O, H, L, C, n), np.sqrt(rs.rolling(n).mean()))
    kk = 0.34 / (1.34 + (n + 1) / (n - 1))
    on = np.log(O / C.shift(1))
    yz = np.sqrt(on.rolling(n).var() + kk * co.rolling(n).var() + (1 - kk) * rs.rolling(n).mean())
    same(ti.yang_zhang(O, H, L, C, n), yz, rtol=1e-7)


def test_relative_strength_and_beta_sanity():
    rs = ti.relative_strength(C, BENCH, 55)
    same(rs, (C / C.shift(55)) / (BENCH / BENCH.shift(55)) - 1)
    assert np.allclose(ti.beta(C, C, 20).dropna(), 1.0)


def test_volume_formulas():
    same(ti.relative_volume(V, 20), V / V.rolling(20).mean())
    tp = (H + L + C) / 3
    same(ti.rolling_vwap(H, L, C, V, 20), (tp * V).rolling(20).sum() / V.rolling(20).sum())
    sv = np.sign(C.diff()) * V
    same(ti.volume_zone_oscillator(C, V), talib.EMA(sv.to_numpy(), 14) / talib.EMA(v, 14) * 100)
    pc = C.shift(1)
    ad = np.where(C > pc, C - np.minimum(L, pc), np.where(C < pc, C - np.maximum(H, pc), 0.0))
    same(ti.williams_ad(H, L, C).iloc[1:], np.cumsum(ad[1:]))


def test_waddah_vfi_wvf_shapes():
    w = ti.waddah_attar_explosion(H, L, C)
    m = talib.EMA(c, 20) - talib.EMA(c, 40)
    t1 = (m - np.r_[np.nan, m[:-1]]) * 150
    same(w.trend_up, np.where(t1 >= 0, t1, 0.0))
    up, mid, lo = talib.BBANDS(c, 20, 2, 2, 0)
    same(w.explosion, up - lo)
    hc = C.rolling(22).max()
    same(ti.williams_vix_fix(L, C).wvf, (hc - L) / hc * 100)


def test_vbt_runs_new_batch():
    from tv_indicators import vbt as tvb

    r = tvb.RANGE_FILTER.run(C, period=[50, 100])
    assert r.filter.shape == (N, 2)
    q = tvb.QQE.run(C, rsi_length=[14, 21], factor=4.238)
    same(q.trailing_line[(14, 4.238)], ti.qqe(C).trailing_line)
