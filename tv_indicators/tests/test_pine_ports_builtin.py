"""Bar-by-bar ports of TradingView *built-in* indicator source, compared with the library.

Sources (fetched 2026-10-28):

* Built-in Pine source: TradingView's own pine-facade API, e.g.
  https://pine-facade.tradingview.com/pine-facade/get/STD%3BKnow_Sure_Thing/last
  (the same text the chart's "Source code" button shows). Script ids and
  versions are given in each test's docstring.
* ``ta.*`` "the same on Pine" reference code and remarks: the Pine v6 reference
  manual data bundled with the Pine editor (static.tradingview.com bundle
  11967.f28d44b63e7af1f5c57f.js plus its en.* string chunks).
* Help Center formula pages (tradingview.com/support/solutions/...), where the
  built-in delegates to an undocumented ``ta.*`` function.

The ports below use only plain Python lists and the Pine semantics:
``na`` compares false, ``x[1]`` is ``na`` on bar 0, ``math.max(na, x)`` is
``na``, ``nz()`` replaces ``na``. They never call library kernels.
"""

import math

import numpy as np
import pandas as pd
import pytest

import tv_indicators as ti
from tv_indicators.tests.test_indicators import C, D, H, L, N, O, V, c, h, isna, l, nz, o, same, v

NA = float("nan")


def close_to(a, b, tail=None):
    same(a, b, tail=tail, rtol=1e-7, atol=1e-9)


# ---------------------------------------------------------------------------
# Pine primitives (plain Python)
# ---------------------------------------------------------------------------

def p_hist(x, i, k):
    """x[k] evaluated on bar i."""
    j = i - k
    return x[j] if j >= 0 else NA


def p_change(x, n=1):
    return [x[i] - x[i - n] if i >= n else NA for i in range(len(x))]


def p_sum(x, n):
    """math.sum; leading na only (na mid-series does not occur in these tests)."""
    out = []
    for i in range(len(x)):
        if i < n - 1:
            out.append(NA)
            continue
        w = x[i - n + 1:i + 1]
        out.append(NA if any(isna(t) for t in w) else sum(w))
    return out


def p_sma(x, n):
    # reference: sum := sum + x[i] / y for i = 0 .. y-1
    out = []
    for i in range(len(x)):
        if i < n - 1:
            out.append(NA)
            continue
        s = 0.0
        for k in range(n):
            s += x[i - k] / n
        out.append(s)  # na propagates
    return out


def p_rma(src, length):
    # reference: sum := na(sum[1]) ? ta.sma(src, length) : alpha * src + (1 - alpha) * nz(sum[1])
    alpha = 1 / length
    sma = p_sma(src, length)
    out = []
    for i in range(len(src)):
        prev = out[i - 1] if i > 0 else NA
        out.append(sma[i] if isna(prev) else alpha * src[i] + (1 - alpha) * nz(prev))
    return out


def p_ema(src, length):
    """ta.ema with an SMA seed over the first `length` non-na values.

    NOTE: the v6 reference's "same on Pine" code seeds with ``src``
    (``sum := na(sum[1]) ? src : ...``), but the real ta.ema returns na for the
    first length-1 bars and seeds with the SMA, like ta.rma's reference. The
    library and every port here use the SMA seed.
    """
    alpha = 2 / (length + 1)
    out, state, buf = [], NA, []
    for x in src:
        if not isna(x):
            if isna(state):
                buf.append(x)
                if len(buf) >= length:
                    state = sum(buf[-length:]) / length
            else:
                state = alpha * x + (1 - alpha) * state
        out.append(state)
    return out


def p_stdev(src, length):
    # reference pine_stdev (biased) with its SUM() epsilon rule
    avg = p_sma(src, length)
    out = []
    for i in range(len(src)):
        if i < length - 1 or isna(avg[i]):
            out.append(NA)
            continue
        ss = 0.0
        for k in range(length):
            r = src[i - k] + (-avg[i])
            if abs(r) <= 1e-10:
                r = 0.0
            ss += r * r
        out.append(math.sqrt(ss / length))
    return out


def p_highest(x, n):
    out = []
    for i in range(len(x)):
        w = x[i - n + 1:i + 1] if i >= n - 1 else None
        out.append(NA if w is None or any(isna(t) for t in w) else max(w))
    return out


def p_lowest(x, n):
    out = []
    for i in range(len(x)):
        w = x[i - n + 1:i + 1] if i >= n - 1 else None
        out.append(NA if w is None or any(isna(t) for t in w) else min(w))
    return out


def p_tr(hh, ll, cc):
    """ta.tr (= ta.tr(false)): na on bar 0."""
    out = []
    for i in range(len(hh)):
        pc = p_hist(cc, i, 1)
        out.append(NA if isna(pc) else max(max(hh[i] - ll[i], abs(hh[i] - pc)), abs(ll[i] - pc)))
    return out


def p_atr(hh, ll, cc, length):
    # reference: trueRange = na(high[1]) ? high-low : max(...); ta.rma(trueRange, length)
    trs = []
    for i in range(len(hh)):
        if isna(p_hist(hh, i, 1)):
            trs.append(hh[i] - ll[i])
        else:
            pc = cc[i - 1]
            trs.append(max(max(hh[i] - ll[i], abs(hh[i] - pc)), abs(ll[i] - pc)))
    return p_rma(trs, length)


def p_swma(x):
    # reference: x[3] * 1 / 6 + x[2] * 2 / 6 + x[1] * 2 / 6 + x[0] * 1 / 6
    return [p_hist(x, i, 3) * 1 / 6 + p_hist(x, i, 2) * 2 / 6 + p_hist(x, i, 1) * 2 / 6 + x[i] * 1 / 6
            for i in range(len(x))]


def p_roc(x, n):
    # "100 * change(src, length) / src[length]"
    return [100 * (x[i] - x[i - n]) / x[i - n] if i >= n else NA for i in range(len(x))]


def p_correlation(x, y, n):
    """Pearson correlation of the last n bars (ta.correlation description)."""
    out = []
    for i in range(len(x)):
        if i < n - 1:
            out.append(NA)
            continue
        xs, ys = x[i - n + 1:i + 1], y[i - n + 1:i + 1]
        mx, my = sum(xs) / n, sum(ys) / n
        sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
        sxx = sum((a - mx) ** 2 for a in xs)
        syy = sum((b - my) ** 2 for b in ys)
        out.append(sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else NA)
    return out


def p_div(a, b):
    return [NA if isna(x) or isna(y) or y == 0 else x / y for x, y in zip(a, b)]


cl, hi, lo, op, vo = list(c), list(h), list(l), list(o), list(v)
hl2 = [(a + b) / 2 for a, b in zip(hi, lo)]
hlc3 = [(a + b + d) / 3 for a, b, d in zip(hi, lo, cl)]


# ---------------------------------------------------------------------------
# Momentum
# ---------------------------------------------------------------------------

def test_kst():
    """STD;Know_Sure_Thing v30: smaroc(roclen, smalen) => ta.sma(ta.roc(close, roclen), smalen)
    kst = smaroc(10,10) + 2*smaroc(15,10) + 3*smaroc(20,10) + 4*smaroc(30,15); sig = ta.sma(kst, 9)."""
    def smaroc(r, s):
        return p_sma(p_roc(cl, r), s)
    a, b, cc_, d = smaroc(10, 10), smaroc(15, 10), smaroc(20, 10), smaroc(30, 15)
    kst = [w + 2 * x + 3 * y + 4 * z for w, x, y, z in zip(a, b, cc_, d)]
    sig = p_sma(kst, 9)
    r = ti.kst(C)
    close_to(r.kst, kst)
    close_to(r.signal, sig)


def test_rvgi():
    """STD;Relative_Vigor_Index v32: rvi = math.sum(ta.swma(close-open), len)/math.sum(ta.swma(high-low), len);
    sig = ta.swma(rvi); len = 10."""
    num = p_sum(p_swma([a - b for a, b in zip(cl, op)]), 10)
    den = p_sum(p_swma([a - b for a, b in zip(hi, lo)]), 10)
    rvi = p_div(num, den)
    r = ti.rvgi(O, H, L, C)
    close_to(r.rvgi, rvi)
    close_to(r.signal, p_swma(rvi))


def _rvi():
    """STD;Relative_Volatility_Index v37: stddev = ta.stdev(close, 10)
    upper = ta.ema(ta.change(src) <= 0 ? 0 : stddev, 14); lower = ta.ema(ta.change(src) > 0 ? 0 : stddev, 14)
    rvi = upper / (upper + lower) * 100."""
    sd = p_stdev(cl, 10)
    ch = p_change(cl)
    up_src = [0.0 if (not isna(x) and x <= 0) else s for x, s in zip(ch, sd)]
    dn_src = [0.0 if (not isna(x) and x > 0) else s for x, s in zip(ch, sd)]
    # On bars 1..8 these inputs mix 0.0 (a real value) with na (stddev not ready).
    # ta.ema remark: "na values in the source series are ignored; the function
    # calculates on the length quantity of non-na values", so the 0.0s count
    # towards the 14-value seed.
    up, dn = p_ema(up_src, 14), p_ema(dn_src, 14)
    return [u / (u + d) * 100 if not (isna(u) or isna(d)) and u + d != 0 else NA for u, d in zip(up, dn)]


def test_relative_volatility_index_exact():
    close_to(ti.relative_volatility_index(C), _rvi())


def test_relative_volatility_index_after_warmup():
    same(ti.relative_volatility_index(C), _rvi(), tail=N - 300, rtol=1e-7)


def _tsi_unit(src, short, long_):
    """ta.tsi(src, short, long) on the [-1, 1] scale (reference: "A value in range [-1, 1]").

    ta.tsi's internals are not published; this follows the built-in
    STD;True%1Strength%1Indicator v31 (double_smooth = ema(ema(x, long), short)),
    divided by 100.
    """
    pc = p_change(src)
    num = p_ema(p_ema(pc, long_), short)
    den = p_ema(p_ema([abs(x) if not isna(x) else NA for x in pc], long_), short)
    return p_div(num, den)


def test_smi_ergodic():
    """STD;SMI_Ergodic_Indicator_Oscillator v32 / STD;SMI_Ergodic_Oscillator v28:
    erg = ta.tsi(close, 5, 20); sig = ta.ema(erg, 5); osc = erg - sig."""
    erg = _tsi_unit(cl, 5, 20)
    sig = p_ema(erg, 5)
    r = ti.smi_ergodic(C)
    close_to(r.smi, erg)
    close_to(r.signal, sig)
    close_to(r.oscillator, [a - b for a, b in zip(erg, sig)])
    assert np.nanmax(np.abs(r.smi)) <= 1.0  # -1..1 scale, not x100


def test_mass_index():
    """STD;Mass%1Index v30: span = high - low
    mi = math.sum(ta.ema(span, 9) / ta.ema(ta.ema(span, 9), 9), 10)."""
    span = [a - b for a, b in zip(hi, lo)]
    e1 = p_ema(span, 9)
    mi = p_sum(p_div(e1, p_ema(e1, 9)), 10)
    close_to(ti.mass_index(H, L), mi)


def _price_osc_current():
    # STD;Price_Oscillator v35 (defaults 12 / 26 / 9, EMA / EMA)
    fast, slow = p_ema(cl, 12), p_ema(cl, 26)
    ppo = [100.0 * (a - b) / b if not (isna(a) or isna(b)) else NA for a, b in zip(fast, slow)]
    sig = p_ema(ppo, 9)
    return ppo, sig, [a - b for a, b in zip(ppo, sig)]


def test_price_oscillator_current_builtin():
    ppo, _, _ = _price_osc_current()
    close_to(ti.price_oscillator(C).ppo, ppo)


def test_price_oscillator_current_builtin_equals_ti_ppo():
    """float ppo = 100.0 * (maFast - maSlow) / maSlow; signal = ma(ppo, 9); hist = ppo - signal."""
    ppo, sig, hist = _price_osc_current()
    r = ti.ppo(C)
    close_to(r.ppo, ppo)
    close_to(r.signal, sig)
    close_to(r.hist, hist)


def test_price_oscillator_legacy_v1():
    """STD;Price_Oscillator v1.0 (2016): short = sma(src, 10); long = sma(src, 21); po = (short - long)/long*100."""
    s, lg = p_sma(cl, 10), p_sma(cl, 21)
    po = [(a - b) / b * 100 if not (isna(a) or isna(b)) else NA for a, b in zip(s, lg)]
    close_to(ti.price_oscillator(C, 10, 21, osc_ma="sma").ppo, po)


def test_bull_bear_power():
    """STD;Bull%Bear%Power v7: bullPower = high - ta.ema(close, 13); bearPower = low - ta.ema(close, 13);
    bbp = bullPower + bearPower (the only plot)."""
    e = p_ema(cl, 13)
    bull = [a - b for a, b in zip(hi, e)]
    bear = [a - b for a, b in zip(lo, e)]
    r = ti.bull_bear_power(H, L, C)
    close_to(r.bull, bull)
    close_to(r.bear, bear)
    close_to(r.bbp, [a + b for a, b in zip(bull, bear)])


def test_awesome_oscillator_part_of_ac():
    """STD;Awesome_Oscillator v31: ao = ta.sma(hl2,5) - ta.sma(hl2,34)."""
    ao = [a - b for a, b in zip(p_sma(hl2, 5), p_sma(hl2, 34))]
    close_to(ti.awesome_oscillator(H, L), ao)


def test_accelerator_oscillator_unverified_formula():
    """SOURCE NOT FOUND: TV's Accelerator Oscillator has no open Pine source (not in
    pine-facade's standard list) and no Help Center formula page. This only checks
    the textbook AC = AO - sma(AO, 5) used by community scripts; it is not a
    verification against TradingView."""
    ao = [a - b for a, b in zip(p_sma(hl2, 5), p_sma(hl2, 34))]
    sm = p_sma(ao, 5)
    close_to(ti.accelerator_oscillator(H, L), [a - b for a, b in zip(ao, sm)])


def test_trend_strength_index():
    """STD;Trend%1Strength%1Index v4: tsi = ta.correlation(close, bar_index, 14)."""
    close_to(ti.trend_strength_index(C), p_correlation(cl, [float(i) for i in range(N)], 14))


def _rci(src, length):
    """Help Center 43000765570: rank prices ascending (ties -> average rank),
    correlation of price ranks with bar indices, x100."""
    out = []
    for i in range(len(src)):
        if i < length - 1:
            out.append(NA)
            continue
        w = src[i - length + 1:i + 1]  # oldest first
        order = sorted(range(length), key=lambda j: w[j])
        ranks = [0.0] * length
        k = 0
        while k < length:
            m = k
            while m + 1 < length and w[order[m + 1]] == w[order[k]]:
                m += 1
            for t in range(k, m + 1):
                ranks[order[t]] = (k + m) / 2
            k = m + 1
        out.append(100 * p_correlation(ranks, [float(j) for j in range(length)], length)[-1])
    return out


@pytest.mark.parametrize("length", [9, 10, 14])
def test_rci_formula(length):
    close_to(ti.rci(C, length), _rci(cl, length))


def test_rci_ties_use_average_rank():
    x = pd.Series([10.0, 12.0, 15.0, 12.0, 11.0, 11.0, 13.0, 9.0, 13.0, 13.0, 14.0, 12.0])
    close_to(ti.rci(x, 4), _rci(list(x), 4))
    # rising prices -> +100 (sign check)
    assert ti.rci(pd.Series(np.arange(20.0)), 10).iloc[-1] == pytest.approx(100.0)


def test_rci_default_length():
    close_to(ti.rci(C), _rci(cl, 10))


def test_balance_of_power():
    """STD;Balance%1of%1Power v30: plot((close - open) / (high - low))."""
    close_to(ti.bop(O, H, L, C), p_div([a - b for a, b in zip(cl, op)], [a - b for a, b in zip(hi, lo)]))


# ---------------------------------------------------------------------------
# Volume
# ---------------------------------------------------------------------------

def _klinger():
    # STD;Klinger%1Oscillator v31: sv = ta.change(hlc3) >= 0 ? volume : -volume
    ch = p_change(hlc3)
    sv = [vv if (not isna(x) and x >= 0) else -vv for x, vv in zip(ch, vo)]  # na >= 0 is false
    kvo = [a - b for a, b in zip(p_ema(sv, 34), p_ema(sv, 55))]
    return kvo, p_ema(kvo, 13)


def test_klinger_exact():
    kvo, sig = _klinger()
    r = ti.klinger(H, L, C, V)
    close_to(r.kvo, kvo)
    close_to(r.signal, sig)


def test_klinger_after_warmup():
    kvo, sig = _klinger()
    r = ti.klinger(H, L, C, V)
    same(r.kvo, kvo, tail=1500, rtol=1e-6)
    same(r.signal, sig, tail=1500, rtol=1e-6)


def test_ease_of_movement():
    """STD;EOM v30: eom = ta.sma(div * ta.change(hl2) * (high - low) / volume, 14), div = 10000."""
    ch = p_change(hl2)
    x = [10000 * a * (b - d) / e if not isna(a) else NA for a, b, d, e in zip(ch, hi, lo, vo)]
    close_to(ti.ease_of_movement(H, L, V), p_sma(x, 14))


def test_net_volume_legacy():
    """STD;Net%1Volume v20 (Pine v4): nv = sign(change(close)) * volume.

    The current v33 script plots `delta` from ta.requestUpAndDownVolume(lower
    timeframe), i.e. up-tick minus down-tick volume of intrabars, which cannot
    be rebuilt from chart OHLCV. ti.net_volume matches the legacy formula only.
    """
    ch = p_change(cl)
    nv = [NA if isna(x) else (1.0 if x > 0 else -1.0 if x < 0 else 0.0) * vv for x, vv in zip(ch, vo)]
    close_to(ti.net_volume(C, V), nv)


def _volume_index(negative):
    # reference f_nvi()/f_pvi(); built-in plots ta.nvi * 1000.0 and ta.ema(nvi, 255)
    out = []
    for i in range(N):
        prev_raw = out[i - 1] if i > 0 else NA
        prev = 1.0 if nz(prev_raw, 0.0) == 0.0 else prev_raw
        c1 = p_hist(cl, i, 1)
        v1 = p_hist(vo, i, 1)
        if nz(cl[i], 0.0) == 0.0 or nz(c1, 0.0) == 0.0:
            cur = prev
        else:
            cond = vo[i] < nz(v1, 0.0) if negative else vo[i] > nz(v1, 0.0)
            cur = prev + ((cl[i] - c1) / c1) * prev if cond else prev
        out.append(cur)
    idx = [x * 1000.0 for x in out]
    return idx, p_ema(idx, 255)


def test_nvi():
    """STD;Negative_Volume_Index v4: nvi = ta.nvi * 1000.0; ema = ta.ema(nvi, 255)."""
    nv, e = _volume_index(True)
    r = ti.nvi(C, V)
    close_to(r.nvi, nv)
    close_to(r.signal, e)


def test_pvi():
    """STD;Positive_Volume_Index v4: pvi = ta.pvi * 1000.0; ema = ta.ema(pvi, 255)."""
    pv, e = _volume_index(False)
    r = ti.pvi(C, V)
    close_to(r.pvi, pv)
    close_to(r.signal, e)


# ---------------------------------------------------------------------------
# Stops / overlays
# ---------------------------------------------------------------------------

def test_volatility_stop():
    """STD;Volatility_Stop v21 (length 20, factor 2.0, src close)."""
    atr = p_atr(hi, lo, cl, 20)
    tr = p_tr(hi, lo, cl)
    stops, ups = [], []
    mx = mn = NA
    uptrend = True
    stop = NA
    prev_up = False  # bool history on bar 0
    for i in range(N):
        src = cl[i]
        if i == 0:
            mx = mn = src  # var max/min = src
        a = atr[i] * 2.0
        atr_m = tr[i] if isna(a) else a  # nz(ta.atr(atrlen) * atrfactor, ta.tr)
        mx = max(mx, src)
        mn = min(mn, src)
        if uptrend:
            cand = NA if isna(stop) or isna(atr_m) else max(stop, mx - atr_m)
        else:
            cand = NA if isna(stop) or isna(atr_m) else min(stop, mn + atr_m)
        stop = src if isna(cand) else cand
        uptrend = src - stop >= 0.0
        if uptrend != prev_up and i > 0:  # and not barstate.isfirst
            mx = mn = src
            stop = mx - atr_m if uptrend else mn + atr_m
        stops.append(stop)
        ups.append(1.0 if uptrend else -1.0)
        prev_up = uptrend
    r = ti.volatility_stop(H, L, C)
    close_to(r.stop, stops)
    close_to(r.trend, ups)


def test_chande_kroll_stop():
    """STD;Chande%1Kroll%1Stop v31 (p=10, x=1, q=9):
    first_high_stop = ta.highest(high, p) - x * ta.atr(p); first_low_stop = ta.lowest(low, p) + x * ta.atr(p)
    stop_short = ta.highest(first_high_stop, q); stop_long = ta.lowest(first_low_stop, q)."""
    atr = p_atr(hi, lo, cl, 10)
    fh = [a - 1 * b for a, b in zip(p_highest(hi, 10), atr)]
    fl = [a + 1 * b for a, b in zip(p_lowest(lo, 10), atr)]
    r = ti.chande_kroll_stop(H, L, C)
    close_to(r.stop_short, p_highest(fh, 9))
    close_to(r.stop_long, p_lowest(fl, 9))


def _pine_sar(start, inc, mx):
    """Pine v6 reference 'The same on Pine Script' for ta.sar."""
    out = []
    result = max_min = acceleration = NA
    is_below = False
    for i in range(N):
        is_first = False
        if i == 1:
            if cl[i] > cl[i - 1]:
                is_below = True
                max_min = hi[i]
                result = lo[i - 1]
            else:
                is_below = False
                max_min = lo[i]
                result = hi[i - 1]
            is_first = True
            acceleration = start
        result = result + acceleration * (max_min - result)
        if is_below:
            if result > lo[i]:
                is_first = True
                is_below = False
                result = max(hi[i], max_min)
                max_min = lo[i]
                acceleration = start
        else:
            if result < hi[i]:
                is_first = True
                is_below = True
                result = min(lo[i], max_min)
                max_min = hi[i]
                acceleration = start
        if not is_first:
            if is_below:
                if hi[i] > max_min:
                    max_min = hi[i]
                    acceleration = min(acceleration + inc, mx)
            else:
                if lo[i] < max_min:
                    max_min = lo[i]
                    acceleration = min(acceleration + inc, mx)
        # reversal check above happens BEFORE this clamp to the prior two bars
        if is_below:
            result = NA if isna(result) else min(result, p_hist(lo, i, 1))
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = NA if isna(result) else max(result, p_hist(hi, i, 1))
            if i > 1:
                result = max(result, hi[i - 2])
        out.append(result)
    return out


@pytest.mark.parametrize("params", [(0.02, 0.02, 0.2), (0.01, 0.03, 0.15)])
def test_sar_reference(params):
    close_to(ti.psar(H, L, C, *params).psar, _pine_sar(*params))


# ---------------------------------------------------------------------------
# Bill Williams
# ---------------------------------------------------------------------------

def _smma(src, length):
    # smma := na(smma[1]) ? ta.sma(src, length) : (smma[1] * (length - 1) + src) / length
    sma = p_sma(src, length)
    out = []
    for i in range(len(src)):
        prev = out[i - 1] if i > 0 else NA
        out.append(sma[i] if isna(prev) else (prev * (length - 1) + src[i]) / length)
    return out


def test_alligator():
    """STD;Williams_Alligator v31: smma(hl2, 13/8/5) plotted with offset 8/5/3 (value under
    bar t was computed on bar t - offset)."""
    def shifted(x, k):
        return [p_hist(x, i, k) for i in range(len(x))]
    r = ti.alligator(H, L)
    close_to(r.jaw, shifted(_smma(hl2, 13), 8))
    close_to(r.teeth, shifted(_smma(hl2, 8), 5))
    close_to(r.lips, shifted(_smma(hl2, 5), 3))


def _pine_fractals(hh, ll, n=2):
    """STD;Whilliams_Fractals v31, literally (flag on the confirming bar; plotted offset=-n)."""
    def g(x, i, k):
        return p_hist(x, i, k)

    def lt(a, b):
        return not (isna(a) or isna(b)) and a < b

    def le(a, b):
        return not (isna(a) or isna(b)) and a <= b

    ups, dns = [], []
    for t in range(len(hh)):
        H_ = lambda k: g(hh, t, k)  # noqa: E731
        L_ = lambda k: g(ll, t, k)  # noqa: E731
        dfront = f0 = f1 = f2 = f3 = f4 = True
        for i in range(1, n + 1):
            dfront = dfront and lt(H_(n - i), H_(n))
            f0 = f0 and lt(H_(n + i), H_(n))
            f1 = f1 and (le(H_(n + 1), H_(n)) and lt(H_(n + i + 1), H_(n)))
            f2 = f2 and (le(H_(n + 1), H_(n)) and le(H_(n + 2), H_(n)) and lt(H_(n + i + 2), H_(n)))
            f3 = f3 and (le(H_(n + 1), H_(n)) and le(H_(n + 2), H_(n)) and le(H_(n + 3), H_(n))
                         and lt(H_(n + i + 3), H_(n)))
            f4 = f4 and (le(H_(n + 1), H_(n)) and le(H_(n + 2), H_(n)) and le(H_(n + 3), H_(n))
                         and le(H_(n + 4), H_(n)) and lt(H_(n + i + 4), H_(n)))
        ups.append(dfront and (f0 or f1 or f2 or f3 or f4))

        dfront = f0 = f1 = f2 = f3 = f4 = True
        for i in range(1, n + 1):
            dfront = dfront and lt(L_(n), L_(n - i))
            f0 = f0 and lt(L_(n), L_(n + i))
            f1 = f1 and (le(L_(n), L_(n + 1)) and lt(L_(n), L_(n + i + 1)))
            f2 = f2 and (le(L_(n), L_(n + 1)) and le(L_(n), L_(n + 2)) and lt(L_(n), L_(n + i + 2)))
            f3 = f3 and (le(L_(n), L_(n + 1)) and le(L_(n), L_(n + 2)) and le(L_(n), L_(n + 3))
                         and lt(L_(n), L_(n + i + 3)))
            f4 = f4 and (le(L_(n), L_(n + 1)) and le(L_(n), L_(n + 2)) and le(L_(n), L_(n + 3))
                         and le(L_(n), L_(n + 4)) and lt(L_(n), L_(n + i + 4)))
        dns.append(dfront and (f0 or f1 or f2 or f3 or f4))
    return np.array(ups), np.array(dns)


def test_fractals_random_data():
    """On data without equal neighbouring highs/lows the two agree."""
    up, dn = _pine_fractals(hi, lo, 2)
    r = ti.fractals(H, L)
    np.testing.assert_array_equal(r.up.to_numpy(), up)
    np.testing.assert_array_equal(r.down.to_numpy(), dn)


def test_fractals_equal_highs_on_left():
    hh = [1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 0.5, 0.4]
    ll = [x - 0.5 for x in [5.0, 4.0, 3.0, 3.0, 4.0, 5.0, 6.0, 7.0]]
    up, dn = _pine_fractals(hh, ll, 2)
    assert up[5] and dn[5]  # TV: fractal on bar 3, confirmed on bar 5
    r = ti.fractals(np.array(hh), np.array(ll))
    np.testing.assert_array_equal(r.up, up)
    np.testing.assert_array_equal(r.down, dn)


# ---------------------------------------------------------------------------
# Pivot Points Standard
# ---------------------------------------------------------------------------

def _pivots(kind):
    """Help Center 43000521824 formulas; prev* = previous daily period, currOpen = current period's open."""
    day = D.index.normalize()
    out = {k: [NA] * N for k in ["p", "r1", "r2", "r3", "s1", "s2", "s3"]}
    prev = None
    cur_h = cur_l = cur_c = cur_o = NA
    for i in range(N):
        if i == 0 or day[i] != day[i - 1]:
            if i > 0:
                prev = (cur_h, cur_l, cur_c)
            cur_h, cur_l, cur_o = hi[i], lo[i], op[i]
        else:
            cur_h, cur_l = max(cur_h, hi[i]), min(cur_l, lo[i])
        cur_c = cl[i]
        if prev is None:
            continue
        ph, pl, pc = prev
        rng = ph - pl
        if kind == "traditional":
            p = (ph + pl + pc) / 3
            lv = dict(p=p, r1=p * 2 - pl, s1=p * 2 - ph, r2=p + rng, s2=p - rng,
                      r3=p * 2 + (ph - 2 * pl), s3=p * 2 - (2 * ph - pl))
        elif kind == "fibonacci":
            p = (ph + pl + pc) / 3
            lv = dict(p=p, r1=p + 0.382 * rng, s1=p - 0.382 * rng, r2=p + 0.618 * rng, s2=p - 0.618 * rng,
                      r3=p + rng, s3=p - rng)
        elif kind == "woodie":
            p = (ph + pl + 2 * cur_o) / 4
            lv = dict(p=p, r1=2 * p - pl, s1=2 * p - ph, r2=p + rng, s2=p - rng,
                      r3=ph + 2 * (p - pl), s3=pl - 2 * (ph - p))
        elif kind == "classic":
            p = (ph + pl + pc) / 3
            lv = dict(p=p, r1=2 * p - pl, s1=2 * p - ph, r2=p + rng, s2=p - rng, r3=p + 2 * rng, s3=p - 2 * rng)
        else:  # camarilla
            p = (ph + pl + pc) / 3
            lv = dict(p=p, r1=pc + 1.1 * rng / 12, s1=pc - 1.1 * rng / 12, r2=pc + 1.1 * rng / 6,
                      s2=pc - 1.1 * rng / 6, r3=pc + 1.1 * rng / 4, s3=pc - 1.1 * rng / 4)
        for k_, val in lv.items():
            out[k_][i] = val
    return out


@pytest.mark.parametrize("kind", ["traditional", "fibonacci", "woodie", "classic", "camarilla"])
def test_pivot_points(kind):
    exp = _pivots(kind)
    r = ti.pivot_points(O, H, L, C, anchor="D", kind=kind)
    for k_ in ["p", "r1", "r2", "r3", "s1", "s2", "s3"]:
        close_to(getattr(r, k_), exp[k_])
