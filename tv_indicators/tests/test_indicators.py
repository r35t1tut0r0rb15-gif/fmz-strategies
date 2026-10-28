"""Accuracy tests.

1. TA-Lib, where its formula is the same as TradingView's. Indicators whose
   only difference is the warm-up seed (ATR, ADX, MACD, ...) are compared
   after they converge.
2. Bar-by-bar Python ports of the Pine source for TradingView-only scripts
   (Supertrend, Chandelier Exit, UT Bot, BBWP, Fisher, ...). These check the
   vectorised / numba code against a line-by-line reading of the Pine code.
3. vectorbt factory behaviour.

Run:  python -m pytest tv_indicators/tests -q
"""

import math

import numpy as np
import pandas as pd
import pytest

import tv_indicators as ti

talib = pytest.importorskip("talib")

N = 3000
TAIL = 1500  # bars compared for seed-dependent indicators


def _data(seed=7):
    rng = np.random.default_rng(seed)
    ret = rng.normal(0, 0.01, N)
    close = 100 * np.exp(np.cumsum(ret))
    open_ = np.r_[close[0], close[:-1]] * (1 + rng.normal(0, 0.002, N))
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.004, N)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.004, N)))
    # a few flat bars and repeated closes to exercise ties and zero ranges
    flat = rng.choice(N, 30, replace=False)
    high[flat] = low[flat] = open_[flat] = close[flat]
    rep = rng.choice(np.arange(1, N), 30, replace=False)
    close[rep] = close[rep - 1]
    high = np.maximum(high, close)
    low = np.minimum(low, close)
    vol = rng.uniform(100, 10_000, N)
    idx = pd.date_range("2023-01-01", periods=N, freq="h")
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": vol}, index=idx)


D = _data()
O, H, L, C, V = (D[c] for c in ["open", "high", "low", "close", "volume"])
o, h, l, c, v = (D[c].to_numpy() for c in ["open", "high", "low", "close", "volume"])


def same(a, b, tail=None, rtol=1e-9, atol=1e-9):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    if tail:
        a, b = a[-tail:], b[-tail:]
    np.testing.assert_array_equal(np.isnan(a), np.isnan(b))
    m = ~np.isnan(a)
    np.testing.assert_allclose(a[m], b[m], rtol=rtol, atol=atol)


# ---------------------------------------------------------------------------
# 1. TA-Lib
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [5, 14, 50])
def test_simple_averages(n):
    same(ti.sma(C, n), talib.SMA(c, n))
    same(ti.wma(C, n), talib.WMA(c, n))
    same(ti.ema(C, n), talib.EMA(c, n))
    same(ti.dema(C, n), talib.DEMA(c, n))
    same(ti.tema(C, n), talib.TEMA(c, n))
    same(ti.lsma(C, n), talib.LINEARREG(c, n))
    same(ti.kama(C, n), talib.KAMA(c, n), tail=TAIL)


def test_rma_is_wilder():
    # RMA(n) == EMA with alpha 1/n == EMA(2n-1)
    same(ti.rma(C, 14), ti.ema(C, 27), tail=TAIL)


@pytest.mark.parametrize("n,mult", [(20, 2.0), (10, 1.5)])
def test_bbands(n, mult):
    up, mid, lo = talib.BBANDS(c, n, mult, mult, 0)
    bb = ti.bbands(C, length=n, mult=mult)
    same(bb.upper, up)
    same(bb.basis, mid)
    same(bb.lower, lo)
    same(ti.bb_percent_b(C, n, mult), (c - lo) / (up - lo))
    same(ti.bbw(C, n, mult).bbw, (up - lo) / mid * 100)


def test_bbands_ema_basis():
    bb = ti.bbands(C, ma_type="EMA")
    same(bb.basis, talib.EMA(c, 20))
    same(bb.upper - bb.basis, 2 * talib.STDDEV(c, 20, 1))


def test_bbands_vwma_basis():
    bb = ti.bbands(C, V, ma_type="VWMA")
    same(bb.basis, talib.SMA(c * v, 20) / talib.SMA(v, 20))


@pytest.mark.parametrize("n", [2, 14])
def test_rsi(n):
    same(ti.rsi(C, n), talib.RSI(c, n))


def test_stoch():
    k_, d_ = talib.STOCH(h, l, c, 14, 1, 0, 3, 0)
    st = ti.stoch(H, L, C)
    # TA-Lib blanks %K until %D exists; TradingView does not.
    same(st.k, k_, tail=N - 20)
    same(st.d, d_)


def test_stoch_rsi():
    fk, fd = talib.STOCHRSI(c, 14, 14, 3, 0)
    st = ti.stoch_rsi(C, k_smoothing=1, d_smoothing=3)
    same(st.k, fk, tail=N - 40)
    same(st.d, fd)


def test_macd():
    m, s, hst = talib.MACD(c, 12, 26, 9)
    r = ti.macd(C)
    same(r.macd, m, tail=TAIL)
    same(r.signal, s, tail=TAIL)
    same(r.hist, hst, tail=TAIL)


def test_misc_oscillators():
    tp = (h + l + c) / 3
    same(ti.cci(ti.hlc3(H, L, C), 20), talib.CCI(h, l, c, 20), rtol=1e-7)
    same(ti.willr(H, L, C), talib.WILLR(h, l, c, 14))
    same(ti.roc(C), talib.ROC(c, 9))
    same(ti.mom(C), talib.MOM(c, 10))
    same(ti.ultimate_oscillator(H, L, C), talib.ULTOSC(h, l, c, 7, 14, 28))
    same(ti.mfi(H, L, C, V), talib.MFI(h, l, c, v, 14), tail=N - 20)
    same(ti.hlc3(H, L, C), tp)
    t = talib.TRIX(c, 18)
    same(ti.trix(C), 10000 * np.log1p(t / 100), tail=TAIL, rtol=1e-7)


def test_atr_family():
    same(ti.true_range(H, L, C)[1:], talib.TRANGE(h, l, c)[1:])
    same(ti.atr(H, L, C), talib.ATR(h, l, c, 14), tail=TAIL)
    same(ti.natr(H, L, C), talib.NATR(h, l, c, 14), tail=TAIL)


def test_dmi():
    r = ti.dmi(H, L, C)
    same(r.plus_di, talib.PLUS_DI(h, l, c, 14), tail=TAIL, rtol=1e-7)
    same(r.minus_di, talib.MINUS_DI(h, l, c, 14), tail=TAIL, rtol=1e-7)
    same(r.adx, talib.ADX(h, l, c, 14), tail=TAIL, rtol=1e-7)


def test_aroon():
    dn, up = talib.AROON(h, l, 14)
    r = ti.aroon(H, L)
    same(r.up, up)
    same(r.down, dn)


def test_psar_close_to_talib():
    # Pine checks for a reversal before clamping SAR to the prior two bars'
    # range, TA-Lib clamps first, so the two differ around some reversals.
    # This only guards against gross errors; the code is a port of Pine's.
    ours = ti.psar(H, L, C).psar.to_numpy()
    agree = np.isclose(ours, talib.SAR(h, l, 0.02, 0.2), rtol=1e-9)[1:]
    assert agree.mean() > 0.85


def test_volume():
    same(ti.accdist(H, L, C, V), talib.AD(h, l, c, v))
    tl = talib.OBV(c, v)
    ours = ti.obv(C, V).to_numpy()
    same(np.diff(ours[1:]), np.diff(tl[1:]))  # same up to the starting offset
    same(ti.chaikin_osc(H, L, C, V), talib.ADOSC(h, l, c, v, 3, 10), tail=TAIL, rtol=1e-6)


# ---------------------------------------------------------------------------
# 2. Bar-by-bar ports of Pine source
# ---------------------------------------------------------------------------

def nz(x, r=0.0):
    return r if x is None or (isinstance(x, float) and math.isnan(x)) else x


def isna(x):
    return x is None or (isinstance(x, float) and math.isnan(x))


def pine_supertrend(factor, period):
    atr = ti.atr(H, L, C, period).to_numpy()
    src = (h + l) / 2
    st_out, dir_out = [], []
    plb = pub = pst = float("nan")
    for i in range(N):
        ub, lb = src[i] + factor * atr[i], src[i] - factor * atr[i]
        p_lb, p_ub = nz(plb), nz(pub)
        c1 = c[i - 1] if i else float("nan")
        lb = lb if (lb > p_lb or c1 < p_lb) else p_lb
        ub = ub if (ub < p_ub or c1 > p_ub) else p_ub
        if i == 0 or isna(atr[i - 1]):
            d = 1
        elif pst == p_ub:
            d = -1 if c[i] > ub else 1
        else:
            d = 1 if c[i] < lb else -1
        st = lb if d == -1 else ub
        st_out.append(st if not isna(atr[i]) else float("nan"))
        dir_out.append(d if not isna(atr[i]) else float("nan"))
        plb, pub, pst = lb, ub, st
    return np.array(st_out), np.array(dir_out)


def test_supertrend():
    st, d = pine_supertrend(3.0, 10)
    r = ti.supertrend(H, L, C)
    same(r.supertrend, st)
    same(r.direction, d)
    same(r.trend, -d)


def test_chandelier():
    n, mult = 22, 3.0
    atr = mult * ti.atr(H, L, C, n).to_numpy()
    hh = C.rolling(n).max().to_numpy()
    ll = C.rolling(n).min().to_numpy()
    longs, shorts, dirs = [], [], []
    pls = pss = float("nan")
    d = 1
    for i in range(N):
        ls, ss = hh[i] - atr[i], ll[i] + atr[i]
        lsp = ls if isna(pls) else pls
        ssp = ss if isna(pss) else pss
        c1 = c[i - 1] if i else float("nan")
        if c1 > lsp:
            ls = float("nan") if isna(ls) or isna(lsp) else max(ls, lsp)
        if c1 < ssp:
            ss = float("nan") if isna(ss) or isna(ssp) else min(ss, ssp)
        d = 1 if c[i] > ssp else (-1 if c[i] < lsp else d)
        longs.append(ls)
        shorts.append(ss)
        dirs.append(d)
        pls, pss = ls, ss
    r = ti.chandelier_exit(H, L, C)
    same(r.long_stop, longs)
    same(r.short_stop, shorts)
    same(r.direction, dirs)
    dd = np.array(dirs)
    np.testing.assert_array_equal(r.buy.to_numpy()[1:], (dd[1:] == 1) & (dd[:-1] == -1))


def test_ut_bot():
    a = 1.0 * ti.atr(H, L, C, 10).to_numpy()
    stop = []
    prev = float("nan")
    for i in range(N):
        p = nz(prev)
        s1 = c[i - 1] if i else float("nan")
        if c[i] > p and s1 > p:
            x = float("nan") if isna(a[i]) else max(p, c[i] - a[i])
        elif c[i] < p and s1 < p:
            x = float("nan") if isna(a[i]) else min(p, c[i] + a[i])
        elif c[i] > p:
            x = c[i] - a[i]
        else:
            x = c[i] + a[i]
        stop.append(x)
        prev = x
    r = ti.ut_bot(H, L, C)
    same(r.trailing_stop, stop)
    s = np.array(stop)
    above = (c[1:] > s[1:]) & (c[:-1] <= s[:-1])
    np.testing.assert_array_equal(r.buy.to_numpy()[1:], (c[1:] > s[1:]) & above)


def test_fisher():
    src = (h + l) / 2
    hi = pd.Series(src).rolling(9).max().to_numpy()
    lo = pd.Series(src).rolling(9).min().to_numpy()
    val = fish = float("nan")
    out = []
    for i in range(N):
        if isna(hi[i]) or hi[i] == lo[i]:
            nv = float("nan")
        else:
            nv = 0.66 * ((src[i] - lo[i]) / (hi[i] - lo[i]) - 0.5) + 0.67 * nz(val)
            nv = 0.999 if nv > 0.99 else (-0.999 if nv < -0.99 else nv)
        nf = float("nan") if isna(nv) else 0.5 * math.log((1 + nv) / (1 - nv)) + 0.5 * nz(fish)
        out.append(nf)
        val, fish = nv, nf
    r = ti.fisher(H, L)
    same(r.fisher, out)
    same(r.trigger.iloc[1:], out[:-1])


def test_bbwp():
    n, lb = 13, 252
    basis = C.rolling(n).mean()
    dev = C.rolling(n).std(ddof=0)
    w = ((basis + dev - (basis - dev)) / basis).to_numpy()
    out = []
    for i in range(N):
        ln = i if i < lb else lb
        if i < n or ln == 0:
            out.append(float("nan"))
            continue
        s = sum(0 if w[i - j] > w[i] else 1 for j in range(1, ln + 1))
        out.append(s / ln * 100)
    same(ti.bbwp(C).bbwp, out, rtol=1e-7)


def test_squeeze_momentum_lazybear():
    n = 20
    basis = C.rolling(n).mean()
    dev = 1.5 * C.rolling(n).std(ddof=0)  # LazyBear's multKC quirk
    tr = ti.true_range(H, L, C, handle_na=False)
    rangema = tr.rolling(n).mean()
    upper_kc, lower_kc = basis + rangema * 1.5, basis - rangema * 1.5
    sqz_on = ((basis - dev) > lower_kc) & ((basis + dev) < upper_kc)
    mid = (H.rolling(n).max() + L.rolling(n).min()) / 2
    x = (C - (mid + basis) / 2).to_numpy()
    val = [float("nan")] * (2 * n - 2)
    xs = np.arange(n)
    for i in range(2 * n - 2, N):
        slope, icpt = np.polyfit(xs, x[i - n + 1:i + 1], 1)
        val.append(icpt + slope * (n - 1))
    r = ti.squeeze_momentum(H, L, C)
    same(r.momentum, val, rtol=1e-6, atol=1e-8)
    np.testing.assert_array_equal(r.sqz_on.to_numpy(), sqz_on.to_numpy())


def test_bbtrend():
    def bb(n):
        m = C.rolling(n).mean()
        s = C.rolling(n).std(ddof=0) * 2
        return m, m + s, m - s

    sm, su, sl = bb(20)
    _, lu, ll = bb(50)
    same(ti.bbtrend(C), ((sl - ll).abs() - (su - lu).abs()) / sm * 100, rtol=1e-7)


def test_connors_rsi():
    ud, prev = [], float("nan")
    for i in range(N):
        p1 = c[i - 1] if i else float("nan")
        if c[i] == p1:
            x = 0.0
        elif c[i] > p1:
            x = 1.0 if nz(prev) <= 0 else nz(prev) + 1
        else:
            x = -1.0 if nz(prev) >= 0 else nz(prev) - 1
        ud.append(x)
        prev = x
    roc1 = C.pct_change().to_numpy() * 100
    pr = [float("nan")] * N
    for i in range(100, N):
        win = roc1[i - 100:i]
        if not np.isnan(win).any():
            pr[i] = 100 * np.sum(win <= roc1[i]) / 100
    exp = (talib.RSI(c, 3) + talib.RSI(np.array(ud), 2) + np.array(pr)) / 3
    same(ti.connors_rsi(C), exp, rtol=1e-7)


def test_hma_alma():
    n = 14
    half = talib.WMA(c, 7)
    full = talib.WMA(c, 14)
    same(ti.hma(C, n), talib.WMA(2 * half - full, 4))  # round(sqrt(14)) = 4
    m, s = 0.85 * (n - 1), n / 6
    w = np.exp(-((np.arange(n) - m) ** 2) / (2 * s * s))
    exp = C.rolling(n).apply(lambda x: np.dot(x, w) / w.sum(), raw=True)
    same(ti.alma(C, n), exp)


def test_keltner_donchian_ichimoku():
    kc = ti.keltner(H, L, C)
    same(kc.upper, talib.EMA(c, 20) + 2 * ti.atr(H, L, C, 10).to_numpy())
    dc = ti.donchian(H, L)
    same(dc.upper, H.rolling(20).max())
    ich = ti.ichimoku(H, L, C)
    t = (H.rolling(9).max() + L.rolling(9).min()) / 2
    kj = (H.rolling(26).max() + L.rolling(26).min()) / 2
    same(ich.tenkan, t)
    same(ich.senkou_a, ((t + kj) / 2).shift(25))


def test_vwap_resets_daily():
    r = ti.vwap(H, L, C, V)
    tp = (H + L + C) / 3
    day = D.index.normalize()
    exp = (tp * V).groupby(day).cumsum() / V.groupby(day).cumsum()
    same(r.vwap, exp)


def test_heikin_ashi():
    ha = ti.heikin_ashi(O, H, L, C)
    hc = (o + h + l + c) / 4
    ho = [(o[0] + c[0]) / 2]
    for i in range(1, N):
        ho.append((ho[-1] + hc[i - 1]) / 2)
    same(ha.close, hc)
    same(ha.open, ho)


# ---------------------------------------------------------------------------
# 3. Types and vectorbt
# ---------------------------------------------------------------------------

def test_types_round_trip():
    df = pd.concat({"a": C, "b": C * 2}, axis=1)
    out = ti.rsi(df)
    assert isinstance(out, pd.DataFrame) and list(out.columns) == ["a", "b"]
    same(out["b"], ti.rsi(C * 2))
    arr = ti.rsi(c)
    assert isinstance(arr, np.ndarray) and arr.ndim == 1
    assert ti.rsi(C).name == "rsi"


def test_vbt_factories():
    vbt = pytest.importorskip("vectorbt")
    from tv_indicators import vbt as tvb

    bb = tvb.BBANDS.run(C, length=[20, 30], mult=[2.0, 2.5], param_product=True)
    assert bb.upper.shape == (N, 4)
    same(bb.upper[(20, 2.0)], ti.bbands(C).upper)
    entries = bb.close_crossed_below(bb.lower)
    assert entries.dtypes.eq(bool).all()

    ema_bb = tvb.BBANDS.run(C, ma_type="ema")
    same(ema_bb.basis, ti.ema(C, 20))

    st = tvb.SUPERTREND.run(H, L, C, factor=[2.0, 3.0])
    same(st.supertrend[3.0], ti.supertrend(H, L, C).supertrend)

    sq = tvb.SQUEEZE_MOMENTUM.run(H, L, C)
    assert sq.sqz_on.dtype == bool

    pf = vbt.Portfolio.from_signals(C, entries[(20, 2.0)], bb.close_crossed_above(bb.upper)[(20, 2.0)])
    assert np.isfinite(pf.total_return())


def test_every_indicator_runs_in_vbt():
    from tv_indicators import vbt as tvb

    cols = {"open": O, "high": H, "low": L, "close": C, "volume": V,
            "session": pd.Series(ti.session_ids(D.index), index=D.index),
            "other": O, "benchmark": O}
    for name, cls in tvb.FACTORIES.items():
        res = cls.run(*[cols[i] for i in cls.input_names])
        for out in cls.output_names:
            assert getattr(res, out).shape[0] == N, name
