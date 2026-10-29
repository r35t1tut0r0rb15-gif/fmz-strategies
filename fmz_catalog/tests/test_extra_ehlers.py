"""Tests for fmz_catalog/extra_ehlers.py.

Each indicator is checked against a literal bar-by-bar Python port of the
strategy's Pine code (or of Ehlers' published EasyLanguage where the copy is
buggy or differs only in warm-up), and against TA-Lib's HT_DCPERIOD for the
homodyne cycle. Ports keep Pine semantics: x[n] is na before bar n, na
arithmetic gives na and na comparisons are false.
"""

import math

import numpy as np
import pandas as pd
import pytest

import fmz_catalog.extra_ehlers as fe
from tv_indicators.tests.test_indicators import TAIL, C, H, L, N, c, h, l, o, same

talib = pytest.importorskip("talib")

nan = math.nan
HL2 = ((H + L) / 2).to_numpy()


def isna(x):
    return x is None or (isinstance(x, float) and math.isnan(x))


def nz(x, r=0.0):
    return r if isna(x) else x


def at(a, i, n=0):
    """Pine ``a[n]`` on bar ``i``."""
    j = i - n
    return a[j] if j >= 0 else nan


def gt(a, b):  # Pine comparison: na -> false
    return not isna(a) and not isna(b) and a > b


def lt(a, b):
    return not isna(a) and not isna(b) and a < b


def ne0(a):
    return not isna(a) and a != 0


def cos_deg(pi, deg):
    return math.cos(pi * deg / 180)


def tail_same(a, b, start, rtol=1e-9, atol=1e-9):
    same(np.asarray(a, float)[start:], np.asarray(b, float)[start:], rtol=rtol, atol=atol)


# ---------------------------------------------------------------------------
# Band-pass / EMD / Super Passband
# ---------------------------------------------------------------------------

def hpotter_bandpass(price, length, delta, pi):
    beta = cos_deg(pi, 360 / length)
    gamma = 1 / cos_deg(pi, 720 * delta / length)
    alpha = gamma - math.sqrt(gamma * gamma - 1)
    bp = [nan] * len(price)
    for i in range(len(price)):
        bp[i] = (0.5 * (1 - alpha) * (price[i] - at(price, i, 2)) + beta * (1 + alpha) * nz(at(bp, i, 1))
                 - alpha * nz(at(bp, i, 2)))
    return np.array(bp)


def test_bandpass_matches_hpotter_with_exact_pi():
    same(fe.ehlers_bandpass(HL2, 20, 0.5), hpotter_bandpass(HL2, 20, 0.5, math.pi))
    same(fe.ehlers_bandpass(C, 30, 0.3), hpotter_bandpass(c, 30, 0.3, math.pi))
    # the recursion itself, with the copies' 3.14 and 3.1415
    for pi in (3.14, 3.1415):
        b = fe._bandpass_nb(HL2.reshape(-1, 1), *fe._bandpass_coefs(20, 0.5, pi))[:, 0]
        same(b, hpotter_bandpass(HL2, 20, 0.5, pi))
    # pi = 3.14 moves the line by a visible amount
    d = np.nanmax(np.abs(hpotter_bandpass(HL2, 20, 0.5, 3.14) - np.asarray(fe.ehlers_bandpass(HL2, 20, 0.5))))
    assert d > 1e-4


def test_emd_matches_hpotter():
    length, delta, frac = 20, 0.5, 0.1
    bp = hpotter_bandpass(HL2, length, delta, math.pi)
    mean = pd.Series(bp).rolling(2 * length).mean().to_numpy()
    pk, vl = [0.0] * N, [0.0] * N
    for i in range(N):
        b0, b1, b2 = bp[i], at(bp, i, 1), at(bp, i, 2)
        pk[i] = b1 if gt(b1, b0) and gt(b1, b2) else nz(at(pk, i, 1))
        vl[i] = b1 if lt(b1, b0) and lt(b1, b2) else nz(at(vl, i, 1))
    up = frac * pd.Series(pk).rolling(50).mean().to_numpy()
    lo = frac * pd.Series(vl).rolling(50).mean().to_numpy()
    pos = [0.0] * N
    for i in range(N):
        pos[i] = (1 if gt(mean[i], up[i]) and gt(mean[i], lo[i]) else
                  -1 if lt(mean[i], up[i]) and lt(mean[i], lo[i]) else nz(at(pos, i, 1)))
    r = fe.ehlers_emd(HL2, length, delta, frac)
    same(r.mean, mean)
    same(r.upper, up)
    same(r.lower, lo)
    same(r.trend, pos)
    assert set(np.unique(pos)) <= {-1.0, 0.0, 1.0} and np.abs(pos).sum() > 100


def test_super_passband_ehlers_and_fmz_copy():
    p1, p2 = 40, 60
    a1, a2 = 5 / p1, 5 / p2
    pb = [nan] * N
    for i in range(N):  # Ehlers TASC Jul 2016, zero-seeded
        pb[i] = ((a1 - a2) * c[i] + (a2 * (1 - a1) - a1 * (1 - a2)) * at(c, i, 1)
                 + ((1 - a1) + (1 - a2)) * nz(at(pb, i, 1)) - (1 - a1) * (1 - a2) * nz(at(pb, i, 2)))
    rms = [math.sqrt(sum(pb[i - j] ** 2 for j in range(50)) / 50) if i >= 50 else nan for i in range(N)]
    r = fe.ehlers_super_passband(C, p1, p2)
    same(r.pb, pb)
    same(r.rms, rms)
    # FMZ "BandPass EOS": PB = 0 until bar > Period1 and RMS = sqrt(sum/40)
    pbc, rmsc = [0.0] * N, [0.0] * N
    for i in range(N):
        if i > p1:
            pbc[i] = ((a1 - a2) * c[i] + (a2 * (1 - a1) - a1 * (1 - a2)) * c[i - 1]
                      + (1 - a1 + 1 - a2) * nz(pbc[i - 1]) - (1 - a1) * (1 - a2) * nz(pbc[i - 2]))
            s = 0.0
            for j in range(50):
                s = s + (at(pbc, i, j) ** 2 if i - j >= 0 else nan)
            rmsc[i] = math.sqrt(s / 40)
    tail_same(r.pb, pbc, N - TAIL)
    tail_same(r.rms.to_numpy() * math.sqrt(50 / 40), rmsc, N - TAIL)


# ---------------------------------------------------------------------------
# Dominant cycle
# ---------------------------------------------------------------------------

PI_PINE = 3.14159265359


def iq_ifm_port(src, maxp, seed, eltrut=False):
    imult, qmult = 0.635, 0.338
    n = len(src)
    P, ip, qu, re, im, de, inst, ln = ([nan] * n for _ in range(8))
    for i in range(n):
        if eltrut:  # f_IQIFM: _src - nz(_src[7]), nz(_v1[4])
            P[i] = src[i] - nz(at(src, i, 7))
            ip[i] = 1.25 * (nz(at(P, i, 4)) - imult * at(P, i, 2)) + imult * nz(at(ip, i, 3))
        else:
            P[i] = src[i] - at(src, i, 7)
            ip[i] = 1.25 * (at(P, i, 4) - imult * at(P, i, 2)) + imult * nz(at(ip, i, 3))
        qu[i] = at(P, i, 2) - qmult * P[i] + qmult * nz(at(qu, i, 2))
        re[i] = 0.2 * (ip[i] * at(ip, i, 1) + qu[i] * at(qu, i, 1)) + 0.8 * nz(at(re, i, 1))
        im[i] = 0.2 * (ip[i] * at(qu, i, 1) - at(ip, i, 1) * qu[i]) + 0.8 * nz(at(im, i, 1))
        de[i] = math.atan(im[i] / re[i]) if ne0(re[i]) else 0.0
        V, ins = 0.0, 0.0
        for j in range(maxp + 1):
            V = V + at(de, i, j)
            if gt(V, 2 * PI_PINE) and ins == 0.0:
                ins = j
        if ins == 0.0:
            ins = nz(at(inst, i, 1))
        inst[i] = ins
        ln[i] = 0.25 * ins + 0.75 * nz(at(ln, i, 1), seed)
    return np.array(ln), np.array(inst)


def test_iq_ifm_matches_fish_net_and_azlema():
    ln, inst = iq_ifm_port(c, 50, 1.0)  # Enhanced Fish Net getIQ (max 50, nz(lenIQ[1], 1))
    r = fe.ehlers_iq_ifm(C, 50, 1.0)
    same(r.period, ln)
    same(r.inst_period, inst)
    ln, _ = iq_ifm_port(c, 60, 0.0)  # Adaptive ZLEMA v2 (range 60)
    same(fe.ehlers_iq_ifm(C, 60).period, ln)
    ln, _ = iq_ifm_port(c, 50, 0.0, eltrut=True)  # Eltrut f_IQIFM: nz() warm-up only
    tail_same(fe.ehlers_iq_ifm(C, 50).period, ln, N - TAIL)


def cosine_ifm_port(src, rng):
    n = len(src)
    v1, s2, s3, de, inst, ln = ([nan] * n for _ in range(6))
    for i in range(n):
        v1[i] = src[i] - at(src, i, 7)
        s2[i] = 0.2 * (at(v1, i, 1) + v1[i]) ** 2 + 0.8 * nz(at(s2, i, 1))
        s3[i] = 0.2 * (at(v1, i, 1) - v1[i]) ** 2 + 0.8 * nz(at(s3, i, 1))
        v2 = math.sqrt(s3[i] / s2[i]) if ne0(s2[i]) else 0.0
        de[i] = 2 * math.atan(v2) if ne0(s3[i]) else 0.0
        v4, ins = 0.0, 0.0
        for j in range(rng + 1):
            v4 = v4 + at(de, i, j)
            if gt(v4, 2 * PI_PINE) and ins == 0.0:
                ins = j - 1
        if ins == 0.0:
            ins = at(inst, i, 1)  # no nz in the copy
        inst[i] = ins
        ln[i] = 0.25 * ins + 0.75 * nz(at(ln, i, 1))
    return np.array(ln)


def test_cosine_ifm_matches_azlema_after_first_cycle():
    for rng in (50, 100):
        ln = cosine_ifm_port(c, rng)
        mine = fe.ehlers_cosine_ifm(C, rng).period.to_numpy()
        first = int(np.argmax(~np.isnan(ln)))
        assert first < 60
        assert np.all(mine[:first] == 0.0)  # Ehlers' Period starts at 0, the copy at na
        same(mine[first:], ln[first:])


def hilbert_port(price, fixed):
    """Enhanced Fish Net ``getHT``; ``fixed`` turns its '=' into ':='. Uses the
    exact pi instead of the copy's 3.14159 in the degree conversion."""
    Imult, Qmult = 0.635, 0.338
    n = len(price)
    v3 = [price[i] - at(price, i, 7) for i in range(n)]
    IP, Q, PH, DP, IPER, PER = ([0.0] * n for _ in range(6))
    for i in range(n):
        Phase = DeltaPhase = InstPeriod = Period = 0.0
        if i > 5:
            IP[i] = 1.25 * (at(v3, i, 4) - Imult * at(v3, i, 2)) + Imult * nz(at(IP, i, 3))
            Q[i] = at(v3, i, 2) - Qmult * v3[i] + Qmult * nz(at(Q, i, 2))
            s = IP[i] + IP[i - 1]
            if gt(abs(s), 0):
                Phase = 180 / math.pi * math.atan(abs((Q[i] + Q[i - 1]) / s))
            if lt(IP[i], 0) and gt(Q[i], 0):
                Phase = 180 - Phase
            if lt(IP[i], 0) and lt(Q[i], 0):
                Phase = 180 + Phase
            if gt(IP[i], 0) and lt(Q[i], 0):
                Phase = 360 - Phase
            DeltaPhase = PH[i - 1] - Phase
            if PH[i - 1] < 90 and Phase > 270:
                DeltaPhase = 360 + PH[i - 1] - Phase
            DeltaPhase = min(max(DeltaPhase, 1), 60)
            DP[i] = DeltaPhase
            v4 = 0.0
            for j in range(51):
                v4 = v4 + at(DP, i, j)
                if gt(v4, 360) and InstPeriod == 0:
                    InstPeriod = j
            if InstPeriod == 0 and fixed:
                InstPeriod = nz(IPER[i - 1])
            Period = 0.25 * InstPeriod + 0.75 * PER[i - 1]
        PH[i], DP[i], IPER[i], PER[i] = Phase, DeltaPhase, InstPeriod, Period
    return np.array(PER)


def test_hilbert_period_fixes_fish_net_bug():
    mine = fe.ehlers_hilbert_period(C).period
    tail_same(mine, hilbert_port(c, True), N - TAIL)
    # The bug only bites when no 360-degree crossing is found within 51 bars:
    # a 20-bar cycle that turns into a 120-bar one.
    t = np.arange(N)
    x = np.where(t < N // 2, 100 + np.sin(2 * np.pi * t / 20), 100 + np.sin(2 * np.pi * t / 120))
    mine = fe.ehlers_hilbert_period(x).period
    fixed, bug = hilbert_port(x, True), hilbert_port(x, False)
    tail_same(mine, fixed, 300)
    assert abs(mine[N // 2 - 100] - 20) < 1 and mine[-1] > 40  # holds the last measured period
    assert bug[-1] < 1e-6  # the copy decays to 0


def homodyne_vawsi_port(price):
    n = len(price)
    S, D, Q1, I1, I2, Q2, RE, IM, PER, SP = ([0.0] * n for _ in range(10))
    for i in range(n):
        adj = 0.075 * nz(at(PER, i, 1)) + 0.54
        if i > 5:
            S[i] = (4 * price[i] + 3 * price[i - 1] + 2 * price[i - 2] + price[i - 3]) / 10
            D[i] = (0.0962 * S[i] + 0.5769 * S[i - 2] - 0.5769 * S[i - 4] - 0.0962 * S[i - 6]) * adj
            Q1[i] = (0.0962 * D[i] + 0.5769 * D[i - 2] - 0.5769 * D[i - 4] - 0.0962 * D[i - 6]) * adj
            I1[i] = D[i - 3]
        f = lambda a: (0.0962 * a[i] + 0.5769 * nz(at(a, i, 2)) - 0.5769 * nz(at(a, i, 4)) - 0.0962 * nz(at(a, i, 6))) * adj
        jI, jQ = f(I1), f(Q1)
        I2[i] = 0.2 * (I1[i] - jQ) + 0.8 * nz(at(I2, i, 1))
        Q2[i] = 0.2 * (Q1[i] + jI) + 0.8 * nz(at(Q2, i, 1))
        re = I2[i] * nz(at(I2, i, 1)) + Q2[i] * nz(at(Q2, i, 1))
        im = I2[i] * nz(at(Q2, i, 1)) - Q2[i] * nz(at(I2, i, 1))
        RE[i] = 0.2 * re + 0.8 * nz(at(RE, i, 1))
        IM[i] = 0.2 * im + 0.8 * nz(at(IM, i, 1))
        p1 = nz(at(PER, i, 1))
        p = 2 * math.pi / math.atan(IM[i] / RE[i]) if IM[i] != 0 and RE[i] != 0 else 0.0
        p = 1.5 * p1 if p > 1.5 * p1 else p
        p = 0.67 * p1 if p < 0.67 * p1 else p
        p = min(max(p, 6), 50)
        PER[i] = 0.2 * p + 0.8 * p1
        SP[i] = 0.33 * PER[i] + 0.67 * nz(at(SP, i, 1))
    return np.array(SP)


def test_homodyne_matches_talib_and_vawsi():
    r = fe.ehlers_homodyne_dc(C)
    same(r.smooth_period, talib.HT_DCPERIOD(c), tail=TAIL, rtol=1e-8)
    tail_same(r.smooth_period, homodyne_vawsi_port(c), N - TAIL, rtol=1e-8)


# ---------------------------------------------------------------------------
# Zero Lag EC
# ---------------------------------------------------------------------------

def zlec_port(src, alpha, gl):
    n = len(src)
    EMA, EC, LE = [nan] * n, [nan] * n, [nan] * n
    for i in range(n):
        a = alpha[i]
        EMA[i] = a * src[i] + (1 - a) * nz(at(EMA, i, 1))
        le, bg = 1000000.0, 0.0
        for g in range(-gl, gl + 1):
            ec = a * (EMA[i] + g / 10 * (src[i] - nz(at(EC, i, 1)))) + (1 - a) * nz(at(EC, i, 1))
            if lt(abs(src[i] - ec), le):
                le, bg = abs(src[i] - ec), g / 10
        EC[i] = a * (EMA[i] + bg * (src[i] - nz(at(EC, i, 1)))) + (1 - a) * nz(at(EC, i, 1))
        LE[i] = le
    return np.array(EC), np.array(EMA), np.array(LE)


def test_zero_lag_ec_matches_azlema():
    ec, ema, le = zlec_port(c, [2 / 21] * N, 15)
    r = fe.ehlers_zero_lag_ec(C, 20, 15)
    same(r.ec, ec)
    same(r.ema, ema)
    same(r.least_error, le)


def test_zero_lag_ec_adaptive_matches_azlema_cos_ifm():
    ln = cosine_ifm_port(c, 100)  # "Adaptive Zero Lag EMA": Period := round(len)
    per = np.array([math.floor(x + 0.5) if not isna(x) else nan for x in ln])
    ec, ema, _ = zlec_port(c, 2 / (per + 1), 15)
    r = fe.ehlers_zero_lag_ec_adaptive(C, per, 15)
    same(r.ec, ec)
    same(r.ema, ema)


def test_cbma_copy_has_no_error_correction():
    # calc_cbma: '=' inside the if declares locals, so bestGain stays 0 and the
    # "EC" is a zero-seeded EMA of ta.ema.
    a = 2 / 12
    ema = talib.EMA(c, 11)
    ec = [nan] * N
    for i in range(N):
        ec[i] = a * (ema[i] + 0.0 * (c[i] - nz(at(ec, i, 1)))) + (1 - a) * nz(at(ec, i, 1))
    good = fe.ehlers_zero_lag_ec(C, 11, 50).ec.to_numpy()
    assert np.nanmean(np.abs(np.array(ec) - c)) > 1.5 * np.nanmean(np.abs(good - c))


# ---------------------------------------------------------------------------
# Butterworth
# ---------------------------------------------------------------------------

def butt2_port(pr, p1, seed):
    Pi = 2 * math.asin(1)
    a1 = math.exp(-math.sqrt(2) * Pi / p1)
    b1 = 2 * a1 * math.cos(Pi / 180 * (math.sqrt(2) * 180 / p1))
    cf1, cf2, cf3 = (1 - b1 + a1 * a1) / 4, b1, -a1 * a1
    out = [nan] * len(pr)
    for i in range(len(pr)):
        if seed and i < 2:
            out[i] = pr[i]
        else:
            out[i] = (cf1 * (pr[i] + 2 * nz(at(pr, i, 1)) + nz(at(pr, i, 2))) + cf2 * nz(at(out, i, 1))
                      + cf3 * nz(at(out, i, 2)))
    return np.array(out)


def test_butterworth2_copies_and_ehlers():
    same(fe.ehlers_butterworth2(C, 20, zero_seed=True), butt2_port(c, 20, False))  # variant_butt2pole
    sm = C.rolling(14).mean()  # na-led input, as the DI-/choppiness copies
    same(fe.ehlers_butterworth2(sm, 30, zero_seed=True), butt2_port(sm.to_numpy(), 30, False))
    same(fe.ehlers_butterworth2(C, 20), butt2_port(c, 20, True))  # Ehlers: CurrentBar < 3 -> price
    tail_same(fe.ehlers_butterworth2(C, 20), butt2_port(c, 20, False), N - TAIL)


def iirma_port(src, n, pi):
    cf = 2 * math.tan(2 * pi * (1 / n) / 2)
    a0 = 8 + 8 * cf + 4 * cf ** 2 + cf ** 3
    a1 = -24 - 8 * cf + 4 * cf ** 2 + 3 * cf ** 3
    a2 = 24 - 8 * cf - 4 * cf ** 2 + 3 * cf ** 3
    a3 = -8 + 8 * cf - 4 * cf ** 2 + cf ** 3
    cc, d0, d1, d2 = cf ** 3 / a0, -a1 / a0, -a2 / a0, -a3 / a0
    out = [nan] * len(src)
    for i in range(len(src)):
        v = (cc * (src[i] + at(src, i, 3)) + 3 * cc * (at(src, i, 1) + at(src, i, 2))
             + d0 * at(out, i, 1) + d1 * at(out, i, 2) + d2 * at(out, i, 3))
        out[i] = nz(v, src[i])
    return np.array(out)


def test_butterworth3_bilinear_and_ehlers():
    same(fe.ehlers_butterworth3(C, 20, "bilinear"), iirma_port(c, 20, math.pi))
    same(fe.ehlers_butterworth3(C, 20, "bilinear"), iirma_port(c, 20, 3.14159), rtol=1e-6)
    p = 20.0
    a = math.exp(-3.14159265358979 / p)
    b = 2 * a * math.cos(math.radians(1.738 * 180 / p))
    c1 = a * a
    k2, k3, k4, k1 = b + c1, -(c1 + b * c1), c1 * c1, (1 - b + c1) * (1 - c1) / 8
    out = [nan] * N
    for i in range(N):
        out[i] = c[i] if i < 3 else (k1 * (c[i] + 3 * c[i - 1] + 3 * c[i - 2] + c[i - 3])
                                     + k2 * out[i - 1] + k3 * out[i - 2] + k4 * out[i - 3])
    same(fe.ehlers_butterworth3(C, 20), out)


# ---------------------------------------------------------------------------
# Optimal tracking filter
# ---------------------------------------------------------------------------

def otf_port(src, rng):
    v1, v2, v3 = [nan] * N, [nan] * N, [nan] * N
    for i in range(N):
        v1[i] = 0.2 * (src[i] - at(src, i, 1)) + 0.8 * nz(at(v1, i, 1))
        v2[i] = 0.1 * rng[i] + 0.8 * nz(at(v2, i, 1))
        lam = abs(v1[i] / v2[i])
        alpha = (-lam ** 2 + math.sqrt(lam ** 4 + 16 * lam ** 2)) / 8
        v3[i] = alpha * src[i] + (1 - alpha) * nz(at(v3, i, 1))
    return np.array(v3)


def test_optimal_tracking_copy_and_ehlers():
    sma = C.rolling(10).mean()
    tr = np.maximum.reduce([h - l, np.abs(h - np.r_[nan, c[:-1]]), np.abs(l - np.r_[nan, c[:-1]])])
    tr[0] = nan  # ta.tr is na on the first bar
    same(fe.ehlers_optimal_tracking(sma, H, L, C, true_range=True), otf_port(sma.to_numpy(), tr))
    same(fe.ehlers_optimal_tracking(HL2, H, L, C), otf_port(HL2, h - l))


# ---------------------------------------------------------------------------
# High-pass, roofing, AGC (Boom Hunter / Early Onset Trend)
# ---------------------------------------------------------------------------

def boom_hunter_port(src, lp, copy_nz):
    pi = 2 * math.asin(1)
    w = 0.707 * 2 * pi / 100
    a = (math.cos(w) + math.sin(w) - 1) / math.cos(w)
    a1 = math.exp(-1.414 * pi / lp)
    b1 = 2 * a1 * math.cos(1.414 * pi / lp)
    c2, c3 = b1, -a1 * a1
    c1 = 1 - c2 - c3
    HP, F, PK, X = ([nan] * N for _ in range(4))
    for i in range(N):
        x1, x2 = (nz(at(src, i, 1)), nz(at(src, i, 2))) if copy_nz else (at(src, i, 1), at(src, i, 2))
        HP[i] = ((1 - a / 2) ** 2 * (src[i] - 2 * x1 + x2) + 2 * (1 - a) * nz(at(HP, i, 1))
                 - (1 - a) ** 2 * nz(at(HP, i, 2)))
        F[i] = c1 * (HP[i] + nz(at(HP, i, 1))) / 2 + c2 * nz(at(F, i, 1)) + c3 * nz(at(F, i, 2))
        pk = 0.991 * nz(at(PK, i, 1))
        if gt(abs(F[i]), pk):
            pk = abs(F[i])
        PK[i] = pk
        X[i] = F[i] / pk if pk != 0 else 0.0
    return np.array(HP), np.array(F), np.array(X)


def test_highpass_roofing_agc():
    hp, f, x = boom_hunter_port(c, 6, False)  # Ehlers: na until close[2]
    same(fe.ehlers_highpass2(C, 100), hp)
    roof = fe.ehlers_roofing_filter(C, 100, 6)
    same(roof, f)
    tail_same(fe.ehlers_agc(roof).normalized, x, 2)  # the copy prints 0 where Filt is still na
    hp, f, x = boom_hunter_port(c, 28, True)  # the copy's nz(close[1]) start-up step
    tail_same(fe.ehlers_highpass2(C, 100), hp, N - TAIL)
    tail_same(fe.ehlers_agc(fe.ehlers_roofing_filter(C, 100, 28)).normalized, x, N - TAIL)


# ---------------------------------------------------------------------------
# Oscillators
# ---------------------------------------------------------------------------

def cyber_port(src, alpha, lag, copy):
    sm = [(src[i] + 2 * at(src, i, 1) + 2 * at(src, i, 2) + at(src, i, 3)) / 6 for i in range(N)]
    cy, sig = [nan] * N, [nan] * N
    for i in range(N):
        start = isna(at(cy, i, 7)) if copy else i < 6
        if start:
            cy[i] = (src[i] - 2 * at(src, i, 1) + at(src, i, 2)) / 4
        else:
            cy[i] = ((1 - 0.5 * alpha) ** 2 * (sm[i] - 2 * sm[i - 1] + sm[i - 2]) + 2 * (1 - alpha) * nz(cy[i - 1])
                     - (1 - alpha) ** 2 * nz(cy[i - 2]))
        a2 = 1 / (lag + 1)
        sig[i] = a2 * cy[i] + (1 - a2) * nz(at(sig, i, 1))
    return np.array(cy), np.array(sig)


def test_cyber_cycle():
    r = fe.ehlers_cyber_cycle(HL2, 0.07, 9)
    cy, sig = cyber_port(HL2, 0.07, 9, False)
    same(r.cycle, cy)
    same(r.signal, sig)
    same(r.trigger, np.r_[nan, cy[:-1]])
    cy, sig = cyber_port(HL2, 0.07, 9, True)  # strategy copy: na(cycle[7]) start-up
    tail_same(r.cycle, cy, N - TAIL)
    tail_same(r.signal, sig, N - TAIL)


def test_smoothed_rsi_matches_hpotter():
    n = 10
    xv = [(c[i] + 2 * at(c, i, 1) + 2 * at(c, i, 2) + at(c, i, 3)) / 6 for i in range(N)]
    up = [xv[i] - at(xv, i, 1) if gt(xv[i], at(xv, i, 1)) else 0.0 for i in range(N)]
    dn = [at(xv, i, 1) - xv[i] if lt(xv[i], at(xv, i, 1)) else 0.0 for i in range(N)]
    cu = pd.Series(up).rolling(n).sum().to_numpy()
    cd = pd.Series(dn).rolling(n).sum().to_numpy()
    res = np.where(cu + cd != 0, cu / (cu + cd), 0.0)
    mine = fe.ehlers_smoothed_rsi(C, n).to_numpy()
    first = 3 + n
    assert np.isnan(mine[:first]).all() and not np.isnan(mine[first:]).any()
    same(mine[first:], res[first:])


def voss_port(src, period, predict, bw, copy):
    order = 3 * predict
    f1 = math.cos(2 * math.pi / period)
    g1 = math.cos(bw * 2 * math.pi / period)
    s1 = 1 / g1 - math.sqrt(1 / (g1 * g1) - 1)
    F, V = [0.0] * N, [0.0] * N
    for i in range(N):
        sumc = 0.0
        for j in range(order):
            sumc += (j + 1) / order * nz(at(V, i, order - j))
        if copy and i <= order:
            F[i] = V[i] = 0.0
            continue
        F[i] = 0.0 if i <= 4 else 0.5 * (1 - s1) * (src[i] - src[i - 2]) + f1 * (1 + s1) * F[i - 1] - s1 * F[i - 2]
        V[i] = (3 + order) / 2 * F[i] - sumc
    return np.array(V), np.array(F)


def test_voss():
    for predict in (3, 4):
        r = fe.ehlers_voss(C, 20, predict, 0.25)
        v, f = voss_port(c, 20, predict, 0.25, False)
        same(r.voss, v)
        same(r.filt, f)
        v, f = voss_port(c, 20, predict, 0.25, True)  # FMZ copy: zero for bar_index <= order
        tail_same(r.voss, v, N - TAIL)
        tail_same(r.filt, f, N - TAIL)


def test_decycler_matches_copy():
    p = 20
    w = 2 * (2 * math.asin(1)) / p
    a = (math.cos(w) + math.sin(w) - 1) / math.cos(w)
    dec = [nan] * N
    for i in range(N):
        dec[i] = a / 2 * (c[i] + nz(at(c, i, 1))) + (1 - a) * nz(at(dec, i, 1))
    same(fe.ehlers_decycler(C, p), dec)


def test_fisher_stoch_rvi_copy():
    p = 10
    co, hl = c - o, h - l
    v1 = [(co[i] + 2 * at(co, i, 1) + 2 * at(co, i, 2) + at(co, i, 3)) / 6 for i in range(N)]
    v2 = [(hl[i] + 2 * at(hl, i, 1) + 2 * at(hl, i, 2) + at(hl, i, 3)) / 6 for i in range(N)]
    num = pd.Series(v1).rolling(p).sum().to_numpy()
    den = pd.Series(v2).rolling(p).sum().to_numpy()
    rvi = np.array([num[i] / den[i] if ne0(den[i]) else 0.0 for i in range(N)])
    lo = pd.Series(rvi).rolling(p).min().to_numpy()
    hi = pd.Series(rvi).rolling(p).max().to_numpy()
    with np.errstate(invalid="ignore", divide="ignore"):
        st = (rvi - lo) / (hi - lo)
    st[~np.isfinite(st)] = nan
    s2 = [(4 * st[i] + 3 * at(st, i, 1) + 2 * at(st, i, 2) + at(st, i, 3)) / 10 for i in range(N)]
    fs = [0.5 * math.log((1 + 1.98 * (x - 0.5)) / (1 - 1.98 * (x - 0.5))) / 2.64 if not isna(x) else nan for x in s2]
    r = fe.ehlers_fisher_stoch(rvi, p, normalize=True)
    tail_same(r.fisher, fs, 40)
    tail_same(r.trigger, np.r_[nan, fs[:-1]], 40)
    same(fe.ehlers_fisher_stoch(C, 10).fisher.to_numpy() / 2.64, fe.ehlers_fisher_stoch(C, 10, True).fisher)


# ---------------------------------------------------------------------------
# Reflex / Trendflex
# ---------------------------------------------------------------------------

def ss_avg(src, period, root2):
    a = math.exp(-root2 * math.pi / period)
    d = 2 * a * math.cos(root2 * math.pi / period)
    g = -a * a
    out = [nan] * len(src)
    for i in range(len(src)):
        out[i] = (1 - d - g) * (src[i] + nz(at(src, i, 1))) * 0.5 + d * nz(at(out, i, 1)) + g * nz(at(out, i, 2))
    return out


def flex_ehlers_port(src, n, reflex):
    f = ss_avg(src, 0.5 * n, math.sqrt(2))
    out, ms = [nan] * N, [nan] * N
    for i in range(N):
        s = nan
        if i >= n:
            slope = (f[i - n] - f[i]) / n
            s = sum((f[i] + j * slope - f[i - j]) if reflex else (f[i] - f[i - j]) for j in range(1, n + 1)) / n
        ms[i] = 0.04 * s * s + 0.96 * nz(at(ms, i, 1))
        out[i] = nan if isna(s) else (s / math.sqrt(ms[i]) if ms[i] != 0 else 0.0)
    return np.array(out)


def test_trendflex_reflex_ehlers():
    same(fe.ehlers_trendflex(C, 20), flex_ehlers_port(c, 20, False))
    same(fe.ehlers_reflex(C, 20), flex_ehlers_port(c, 20, True))


def test_trendflex_tfo_copy():
    pss, ptf, pema = 8.0, 14, 33
    al = math.sqrt(8.0) * math.asin(1.0) / pss
    be = math.exp(-al)
    ga = -be * be
    de = 2.0 * be * math.cos(al)
    ss, ema, out = [nan] * N, [nan] * N, [nan] * N
    for i in range(N):
        ss[i] = (1.0 - de - ga) * (c[i] + nz(at(c, i, 1))) * 0.5 + de * nz(at(ss, i, 1)) + ga * nz(at(ss, i, 2))
        E = sum(ss[i] - nz(at(ss, i, j)) for j in range(1, ptf + 1))
        eps = E / ptf
        z = 2.0 / (pema + 1.0)
        ema[i] = z * eps * eps + (1.0 - z) * nz(at(ema, i, 1))
        out[i] = 0.0 if ema[i] == 0.0 else eps / math.sqrt(ema[i])
    tail_same(fe.ehlers_trendflex(C, ptf, pss, 2.0 / (pema + 1)), out, N - TAIL)


def test_reflex_eltrut_copy_loop():
    n = 20
    pi = 2 * math.asin(1)
    a = math.exp(-math.sqrt(2) * pi / n)
    c2 = 2 * a * math.cos(math.sqrt(2) * pi / n)
    c3 = -a * a
    c1 = 1 - c2 - c3
    ss = [nan] * N
    for i in range(N):
        ss[i] = (c1 * c[i] + c2 * nz(at(ss, i, 1), nz(at(c, i, 1), c[i]))
                 + c3 * nz(at(ss, i, 2), nz(at(c, i, 2), nz(at(c, i, 1), c[i]))))
    for reflex in (True, False):
        out, ms = [nan] * N, [nan] * N
        for i in range(N):
            slope = (at(ss, i, n) - ss[i]) / n
            s = 0.0
            for j in range(1, n + 1):
                s = s + ((ss[i] + j * slope - at(ss, i, j)) if reflex else (ss[i] - at(ss, i, j)))
            s = s / n
            ms[i] = 0.04 * s ** 2 + 0.96 * nz(at(ms, i, 1))
            out[i] = s / math.sqrt(nz(ms[i])) if ne0(ms[i]) else 0.0
        loop = fe._flex_nb(np.array(ss).reshape(-1, 1), n, 0.04, reflex)[:, 0]
        tail_same(loop, out, n)  # same loop; the copy prints 0 where this is na
        mine = (fe.ehlers_reflex if reflex else fe.ehlers_trendflex)(C, n).to_numpy()
        assert np.nanmax(np.abs(mine[-TAIL:] - np.array(out)[-TAIL:])) > 0.1  # copy's smoother differs


# ---------------------------------------------------------------------------
# HPotter: DELI, Ergodic MDI
# ---------------------------------------------------------------------------

def sign_state(x, ref):
    pos = [0.0] * N
    for i in range(N):
        pos[i] = 1 if gt(x[i], ref[i]) else -1 if lt(x[i], ref[i]) else nz(at(pos, i, 1))
    return pos


def test_deli_hpotter():
    n = 7
    dsp = talib.EMA(HL2, n) - talib.EMA(HL2, 2 * n)
    d = dsp - talib.EMA(dsp, n)
    r = fe.deli(HL2, n)
    same(r.dsp, dsp, rtol=1e-8)
    same(r.deli, d, rtol=1e-7, atol=1e-9)
    same(r.pos, sign_state(d, [0.0] * N))


def test_ergodic_mdi_hpotter():
    r_, s_, u_ = 32, 5, 5
    mdi = c - talib.EMA(c, r_)
    erg = talib.EMA(talib.EMA(mdi, s_), u_)
    sig = talib.EMA(erg, u_)
    r = fe.ergodic_mdi(C, r_, s_, u_)
    same(r.ergodic, erg, rtol=1e-7, atol=1e-9)
    same(r.signal, sig, rtol=1e-7, atol=1e-9)
    same(r.pos, sign_state(erg, sig))


def test_registry_and_vbt_shapes():
    import tv_indicators
    assert "EHLERS_BANDPASS" not in tv_indicators._core.REGISTRY
    assert len(fe.EXTRA_EHLERS) == len(fe.__all__)
    df = pd.DataFrame({"a": c, "b": c[::-1].copy()}, index=C.index)
    out = fe.ehlers_bandpass(df, 20, 0.5)
    assert out.shape == df.shape
    same(out["b"], fe.ehlers_bandpass(c[::-1].copy(), 20, 0.5))
