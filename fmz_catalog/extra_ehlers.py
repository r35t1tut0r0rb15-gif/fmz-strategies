"""Staging area: John Ehlers' filters and cycle measures that FMZ strategies use
and ``tv_indicators`` does not have yet (plus two HPotter/Blau indicators that
the catalog filed under "Ehlers").

Same conventions as ``fmz_catalog.extra``: importing this module moves its
indicators into ``EXTRA_EHLERS`` instead of the main registry. Every function
takes pandas/numpy input, returns the same type, and documents its source and
how it differs from the strategy copies.

Choices that apply to the whole module:

* Pine semantics: ``x[n]`` is na before bar n and na comparisons are false.
  Band-pass / high-pass filters are na until the input history they difference
  exists; low-pass recursions seed their own history with ``nz`` (0), exactly
  like Ehlers' EasyLanguage variables, unless the docstring says otherwise.
* Angles: Ehlers' EasyLanguage works in degrees, Pine in radians. Every angle
  here is in radians with the exact ``math.pi``; the HPotter copies that write
  ``3.14 * deg / 180`` or ``3.1415 * ...`` are slightly off (recorded in the
  report).
* sqrt(2): Ehlers prints it as 1.414 (and 1/sqrt(2) as .707). We use whichever
  the strategy copies use (1.414/.707 for the roofing / high-pass family,
  exact sqrt(2) for Butterworth, Reflex and Trendflex); the two differ by
  1.5e-5 relative.

    import fmz_catalog.extra_ehlers as fe
    bp = fe.ehlers_bandpass((df.high + df.low) / 2, 20, 0.5)
"""

import math

import numpy as np
from numba import njit

from tv_indicators import kernels as k
from tv_indicators._core import REGISTRY, indicator, shift_2d

NAN = np.nan
_BEFORE = set(REGISTRY)

_SQRT2 = math.sqrt(2.0)


# ---------------------------------------------------------------------------
# Small shared kernels
# ---------------------------------------------------------------------------

@njit(cache=True)
def _nz(x):
    return 0.0 if np.isnan(x) else x


@njit(cache=True)
def _lp2_nb(x, c1, c2, c3, avg):
    """y = c1*x' + c2*nz(y[1]) + c3*nz(y[2]); x' = (x + nz(x[1]))/2 when ``avg``.

    NaN input gives NaN output; the next bar treats it as 0 (``nz``)."""
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        y1 = NAN
        y2 = NAN
        for i in range(x.shape[0]):
            v = x[i, c]
            if not np.isnan(v):
                if avg:
                    v = (v + (_nz(x[i - 1, c]) if i > 0 else 0.0)) / 2.0
                v = c1 * v + c2 * _nz(y1) + c3 * _nz(y2)
            out[i, c] = v
            y2 = y1
            y1 = v
    return out


def _ssf_coefs(length, root2):
    a1 = math.exp(-root2 * math.pi / length)
    c2 = 2 * a1 * math.cos(root2 * math.pi / length)
    c3 = -a1 * a1
    return 1 - c2 - c3, c2, c3


def _supersmoother_2d(x, length, root2=1.414):
    """Ehlers' 2-pole Super Smoother on (x + x[1])/2 (Cycle Analytics / TASC)."""
    c1, c2, c3 = _ssf_coefs(float(length), root2)
    return _lp2_nb(x, c1, c2, c3, True)


# ---------------------------------------------------------------------------
# Band-pass, EMD, Super Passband
# ---------------------------------------------------------------------------

def _bandpass_coefs(length, delta, pi=math.pi):
    """beta = cos(360/P), gamma = 1/cos(720*delta/P), alpha = gamma - sqrt(gamma^2-1).

    ``pi`` only exists so the tests can reproduce the copies' 3.14 / 3.1415."""
    beta = math.cos(2 * pi / length)
    gamma = 1.0 / math.cos(4 * pi * delta / length)
    alpha = gamma - math.sqrt(gamma * gamma - 1.0)
    return beta, alpha


@njit(cache=True)
def _bandpass_nb(x, beta, alpha):
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        y1 = NAN
        y2 = NAN
        for i in range(x.shape[0]):
            v = NAN
            if i >= 2 and not np.isnan(x[i, c]) and not np.isnan(x[i - 2, c]):
                v = (0.5 * (1 - alpha) * (x[i, c] - x[i - 2, c])
                     + beta * (1 + alpha) * _nz(y1) - alpha * _nz(y2))
            out[i, c] = v
            y2 = y1
            y1 = v
    return out


def _bandpass_2d(x, length, delta):
    beta, alpha = _bandpass_coefs(float(length), float(delta))
    return _bandpass_nb(x, beta, alpha)


@indicator("EHLERS_BANDPASS", ["close"], ["bp"])
def ehlers_bandpass(close, length=20, delta=0.5):
    """Ehlers band-pass filter centred on ``length`` bars, half bandwidth ``delta``
    (Ehlers & Way, "Empirical Mode Decomposition", TASC Mar 2010; Cycle
    Analytics' ``Bandwidth`` = 2*delta). HPotter's ports use pi = 3.14 / 3.1415
    in the degree conversion; this uses the exact pi. Ehlers' price is hl2."""
    return _bandpass_2d(close, length, delta)


@njit(cache=True)
def _peak_valley_nb(bp):
    pk = np.full(bp.shape, NAN)
    vl = np.full(bp.shape, NAN)
    for c in range(bp.shape[1]):
        p = 0.0
        v = 0.0
        for i in range(bp.shape[0]):
            if i >= 2:
                b0, b1, b2 = bp[i, c], bp[i - 1, c], bp[i - 2, c]
                if b1 > b0 and b1 > b2:
                    p = b1
                if b1 < b0 and b1 < b2:
                    v = b1
            pk[i, c] = p
            vl[i, c] = v
    return pk, vl


@njit(cache=True)
def _band_state_nb(x, up, lo):
    """1 when x is above both lines, -1 when below both, else previous (0 at start)."""
    out = np.zeros(x.shape)
    for c in range(x.shape[1]):
        pos = 0.0
        for i in range(x.shape[0]):
            a, u, l_ = x[i, c], up[i, c], lo[i, c]
            if a > u and a > l_:
                pos = 1.0
            elif a < u and a < l_:
                pos = -1.0
            out[i, c] = pos
    return out


@indicator("EHLERS_EMD", ["close"], ["mean", "upper", "lower", "trend", "bp"])
def ehlers_emd(close, length=20, delta=0.5, fraction=0.1, avg_length=50):
    """Ehlers & Way Empirical Mode Decomposition (TASC Mar 2010): trend
    ``mean`` = sma(bandpass, 2*length) against ``fraction`` x the 50-bar average
    of the band-pass peaks (``upper``) and valleys (``lower``).

    ``trend`` is HPotter's state: 1 above both thresholds, -1 below both, else
    the previous value. ``mean`` alone is HPotter's "ETT". Exact pi (the copies
    use 3.1415); otherwise bar for bar with HPotter's EMD.
    """
    bp = _bandpass_2d(close, length, delta)
    mean = k.sma_nb(bp, 2 * int(length))
    pk, vl = _peak_valley_nb(bp)
    up = fraction * k.sma_nb(pk, int(avg_length))
    lo = fraction * k.sma_nb(vl, int(avg_length))
    return mean, up, lo, _band_state_nb(mean, up, lo), bp


@njit(cache=True)
def _super_passband_nb(x, a1, a2):
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        y1 = NAN
        y2 = NAN
        for i in range(x.shape[0]):
            v = NAN
            if i >= 1 and not np.isnan(x[i, c]) and not np.isnan(x[i - 1, c]):
                v = ((a1 - a2) * x[i, c] + (a2 * (1 - a1) - a1 * (1 - a2)) * x[i - 1, c]
                     + ((1 - a1) + (1 - a2)) * _nz(y1) - (1 - a1) * (1 - a2) * _nz(y2))
            out[i, c] = v
            y2 = y1
            y1 = v
    return out


@indicator("EHLERS_SUPER_PASSBAND", ["close"], ["pb", "rms"])
def ehlers_super_passband(close, fast_length=40, slow_length=60, rms_length=50):
    """Ehlers Super Passband filter (TASC Jul 2016): difference of two
    zero-lag EMAs with a1 = 5/fast, a2 = 5/slow; ``rms`` = sqrt(sum(pb^2, 50)/50).

    The FMZ copy ("BandPass EOS") divides the 50-bar sum by 40, inflating RMS
    by sqrt(50/40), and zeroes PB for the first ``fast`` bars.
    """
    pb = _super_passband_nb(close, 5.0 / fast_length, 5.0 / slow_length)
    n = int(rms_length)
    return pb, np.sqrt(k.sum_nb(pb * pb, n) / n)


# ---------------------------------------------------------------------------
# Dominant-cycle measurement
# ---------------------------------------------------------------------------

@njit(cache=True)
def _accumulate_nb(dp, i, c, limit, max_count, offset):
    """Ehlers' loop: ``For count = 0 to max: Value4 += dp[count]; If Value4 >
    limit and Inst = 0 then Inst = count - offset``. 0 if never reached. Bars
    before the first one end the search (Pine: the sum turns na)."""
    v = 0.0
    res = 0.0
    for j in range(max_count + 1):
        if i - j < 0:
            break
        v += dp[i - j, c]
        if v > limit and res == 0.0:
            res = float(j - offset)
    return res


@njit(cache=True)
def _iq_ifm_nb(x, max_count, seed):
    n, m = x.shape
    per_o = np.full(x.shape, NAN)
    inst_o = np.full(x.shape, NAN)
    imult, qmult = 0.635, 0.338
    for c in range(m):
        v1 = np.full(n, NAN)
        ip = np.full(n, NAN)
        qu = np.full(n, NAN)
        dp = np.zeros((n, 1))
        re = NAN
        im = NAN
        d = 0.0
        inst = 0.0
        per = NAN
        for i in range(n):
            if i >= 7:
                v1[i] = x[i, c] - x[i - 7, c]
            if i >= 4:
                ip[i] = 1.25 * (v1[i - 4] - imult * v1[i - 2]) + imult * (_nz(ip[i - 3]) if i >= 3 else 0.0)
            if i >= 2:
                qu[i] = v1[i - 2] - qmult * v1[i] + qmult * _nz(qu[i - 2])
            if i >= 1:
                re = 0.2 * (ip[i] * ip[i - 1] + qu[i] * qu[i - 1]) + 0.8 * _nz(re)
                im = 0.2 * (ip[i] * qu[i - 1] - ip[i - 1] * qu[i]) + 0.8 * _nz(im)
            if not np.isnan(re) and re != 0.0 and not np.isnan(im):
                d = math.atan(im / re)
            dp[i, 0] = d
            got = _accumulate_nb(dp, i, 0, 2 * math.pi, max_count, 0)
            if got != 0.0:
                inst = got
            per = 0.25 * inst + 0.75 * (seed if np.isnan(per) else per)
            per_o[i, c] = per
            inst_o[i, c] = inst
    return per_o, inst_o


@indicator("EHLERS_IQ_IFM", ["close"], ["period", "inst_period"])
def ehlers_iq_ifm(close, max_count=50, seed=0.0):
    """Ehlers I-Q IFM dominant-cycle period ("Measuring Cycles", 1999, SideBar 1):
    in-phase/quadrature of price - price[7], phase rate atan(Im/Re) summed until
    it passes 2*pi; period = .25*inst + .75*period[1]. Ehlers uses hl2 and sums
    51 bars (``max_count`` = 50; the copies use 50, 60 or an input).

    Faithful to the Fish Net / Adaptive ZLEMA / Eltrut copies after warm-up;
    ``seed=1`` reproduces Fish Net's ``nz(lenIQ[1], 1)``. Their ``min``/``max``
    clamps are left to the caller.
    """
    return _iq_ifm_nb(close, int(max_count), float(seed))


@njit(cache=True)
def _cos_ifm_nb(x, max_count):
    n, m = x.shape
    per_o = np.full(x.shape, NAN)
    inst_o = np.full(x.shape, NAN)
    for c in range(m):
        dp = np.zeros((n, 1))
        s2 = NAN
        s3 = NAN
        v2 = 0.0
        d = 0.0
        inst = 0.0
        per = 0.0
        for i in range(n):
            if i >= 8:
                a = x[i, c] - x[i - 7, c]
                b = x[i - 1, c] - x[i - 8, c]
                s2 = 0.2 * (b + a) * (b + a) + 0.8 * _nz(s2)
                s3 = 0.2 * (b - a) * (b - a) + 0.8 * _nz(s3)
            if not np.isnan(s2) and s2 != 0.0 and not np.isnan(s3):
                v2 = math.sqrt(s3 / s2)
            if not np.isnan(s3) and s3 != 0.0:
                d = 2.0 * math.atan(v2)
            dp[i, 0] = d
            got = _accumulate_nb(dp, i, 0, 2 * math.pi, max_count, 1)
            if got != 0.0:
                inst = got
            per = 0.25 * inst + 0.75 * per
            per_o[i, c] = per
            inst_o[i, c] = inst
    return per_o, inst_o


@indicator("EHLERS_COSINE_IFM", ["close"], ["period", "inst_period"])
def ehlers_cosine_ifm(close, max_count=50):
    """Ehlers Cosine IFM dominant-cycle period ("Measuring Cycles", 1999): phase
    rate 2*atan(sqrt(S3/S2)) of price - price[7], summed until 2*pi, instant
    period = count - 1, smoothed .25/.75. Ehlers sums 51 bars (``max_count``=50).

    The Adaptive ZLEMA copies loop to 100 or 60 and write ``inst := inst[1]``
    without nz, so their period is na (here 0) until the first cycle is found.
    """
    return _cos_ifm_nb(close, int(max_count))


@njit(cache=True)
def _hilbert_phase_nb(x, max_count):
    n, m = x.shape
    per_o = np.full(x.shape, NAN)
    inst_o = np.full(x.shape, NAN)
    imult, qmult = 0.635, 0.338
    for c in range(m):
        v3 = np.full(n, NAN)
        ip = np.full(n, NAN)
        qu = np.full(n, NAN)
        dp = np.zeros((n, 1))
        ph = 0.0
        ph_prev = 0.0
        inst = 0.0
        per = 0.0
        for i in range(n):
            if i >= 7:
                v3[i] = x[i, c] - x[i - 7, c]
            if i >= 4:
                ip[i] = 1.25 * (v3[i - 4] - imult * v3[i - 2]) + imult * _nz(ip[i - 3])
            if i >= 2:
                qu[i] = v3[i - 2] - qmult * v3[i] + qmult * _nz(qu[i - 2])
            I0 = ip[i]
            Q0 = qu[i]
            I1 = ip[i - 1] if i >= 1 else NAN
            Q1 = qu[i - 1] if i >= 1 else NAN
            s = I0 + I1
            if abs(s) > 0:
                ph = math.degrees(math.atan(abs((Q0 + Q1) / s)))
            if I0 < 0 and Q0 > 0:
                ph = 180.0 - ph
            if I0 < 0 and Q0 < 0:
                ph = 180.0 + ph
            if I0 > 0 and Q0 < 0:
                ph = 360.0 - ph
            d = ph_prev - ph
            if ph_prev < 90 and ph > 270:
                d = 360.0 + ph_prev - ph
            d = min(max(d, 1.0), 60.0)
            dp[i, 0] = d
            ph_prev = ph
            got = _accumulate_nb(dp, i, 0, 360.0, max_count, 0)
            if got != 0.0:
                inst = got
            per = 0.25 * inst + 0.75 * per
            per_o[i, c] = per
            inst_o[i, c] = inst
    return per_o, inst_o


@indicator("EHLERS_HILBERT_PERIOD", ["close"], ["period", "inst_period"])
def ehlers_hilbert_period(close, max_count=50):
    """Ehlers' original phase-accumulation cycle measurer (the "original
    approach" of "Measuring Cycles", 1999; MESA "Market Mode Strategies"): phase
    from the Imult .635 / Qmult .338 Hilbert pair, delta phase clamped to
    [1, 60] degrees, summed until 360. ProRealCode's Sinewave listing sums 41
    bars, the Fish Net copy 51 (default here).

    Fixes the Fish Net copy (``getHT``): its ``InstPeriod = nz(InstPeriod[1])``
    declares a new local, so the previous period is never carried over and the
    period decays toward 0 on bars where no 360-degree crossing is found.
    """
    return _hilbert_phase_nb(close, int(max_count))


@njit(cache=True)
def _homodyne_nb(price):
    n, m = price.shape
    per_o = np.full(price.shape, NAN)
    sper_o = np.full(price.shape, NAN)
    for c in range(m):
        sm = np.zeros(n)
        de = np.zeros(n)
        q1 = np.zeros(n)
        i1 = np.zeros(n)
        i2 = 0.0
        q2 = 0.0
        re = 0.0
        im = 0.0
        per = 0.0
        sper = 0.0
        for i in range(6, n):
            p = price[i, c]
            if np.isnan(p) or np.isnan(price[i - 3, c]):
                continue
            adj = 0.075 * per + 0.54
            sm[i] = (4 * p + 3 * price[i - 1, c] + 2 * price[i - 2, c] + price[i - 3, c]) / 10
            de[i] = (0.0962 * sm[i] + 0.5769 * sm[i - 2] - 0.5769 * sm[i - 4] - 0.0962 * sm[i - 6]) * adj
            q1[i] = (0.0962 * de[i] + 0.5769 * de[i - 2] - 0.5769 * de[i - 4] - 0.0962 * de[i - 6]) * adj
            i1[i] = de[i - 3]
            ji = (0.0962 * i1[i] + 0.5769 * i1[i - 2] - 0.5769 * i1[i - 4] - 0.0962 * i1[i - 6]) * adj
            jq = (0.0962 * q1[i] + 0.5769 * q1[i - 2] - 0.5769 * q1[i - 4] - 0.0962 * q1[i - 6]) * adj
            i2n = 0.2 * (i1[i] - jq) + 0.8 * i2
            q2n = 0.2 * (q1[i] + ji) + 0.8 * q2
            re = 0.2 * (i2n * i2 + q2n * q2) + 0.8 * re
            im = 0.2 * (i2n * q2 - q2n * i2) + 0.8 * im
            i2 = i2n
            q2 = q2n
            pr = per
            if im != 0 and re != 0:
                pr = 2 * math.pi / math.atan(im / re)
            if pr > 1.5 * per:
                pr = 1.5 * per
            if pr < 0.67 * per:
                pr = 0.67 * per
            pr = min(max(pr, 6.0), 50.0)
            per = 0.2 * pr + 0.8 * per
            sper = 0.33 * per + 0.67 * sper
            per_o[i, c] = per
            sper_o[i, c] = sper
    return per_o, sper_o


@indicator("EHLERS_HOMODYNE_DC", ["close"], ["period", "smooth_period"])
def ehlers_homodyne_dc(close):
    """Ehlers Hilbert-transform homodyne dominant cycle ("Rocket Science for
    Traders", 2001, ch. 7): the MAMA period engine. ``smooth_period`` converges
    to TA-Lib ``HT_DCPERIOD``. The VAWSI copy (BlackCat1402's ``EhlersHoDyDC``)
    is faithful; it then takes ceil(1.1*smooth_period) clamped to [1, 34]."""
    return _homodyne_nb(close)


# ---------------------------------------------------------------------------
# Zero Lag (error-correcting) EMA
# ---------------------------------------------------------------------------

@njit(cache=True)
def _zlec_nb(x, alpha, gain_limit):
    shape = x.shape
    ec_o = np.full(shape, NAN)
    ema_o = np.full(shape, NAN)
    le_o = np.full(shape, NAN)
    bg_o = np.full(shape, NAN)
    for c in range(shape[1]):
        ema = NAN
        ec = NAN
        for i in range(shape[0]):
            s = x[i, c]
            a = alpha[i, c]
            if np.isnan(s) or np.isnan(a):
                ema = NAN
                ec = NAN
                continue
            ema = a * s + (1 - a) * _nz(ema)
            e1 = _nz(ec)
            least = 1000000.0
            best = 0.0
            for g in range(-gain_limit, gain_limit + 1):
                gain = g / 10.0
                err = abs(s - (a * (ema + gain * (s - e1)) + (1 - a) * e1))
                if err < least:
                    least = err
                    best = gain
            ec = a * (ema + best * (s - e1)) + (1 - a) * e1
            ec_o[i, c] = ec
            ema_o[i, c] = ema
            le_o[i, c] = least
            bg_o[i, c] = best
    return ec_o, ema_o, le_o, bg_o


@indicator("EHLERS_ZERO_LAG_EC", ["close"], ["ec", "ema", "least_error", "best_gain"])
def ehlers_zero_lag_ec(close, length=20, gain_limit=50):
    """Ehlers & Way Zero Lag (error-correcting) EMA, TASC Nov 2010 "Zero Lag
    (Well, Almost)": EC = a*(EMA + g*(src - EC[1])) + (1-a)*EC[1], with the gain
    g in [-limit/10, limit/10] (step .1) that minimises |src - EC|. Zero-seeded
    EMA, as published. Bar for bar with the Adaptive ZLEMA copies.

    The CBMA copy is broken: one gain only, and ``bestGain = gain`` inside the
    if-block declares a local, so its "EC" is a plain EMA of ta.ema.
    """
    a = np.full(close.shape, 2.0 / (length + 1.0))
    return _zlec_nb(close, a, int(gain_limit))


@indicator("EHLERS_ZERO_LAG_EC_ADAPTIVE", ["close", "period"], ["ec", "ema", "least_error", "best_gain"])
def ehlers_zero_lag_ec_adaptive(close, period, gain_limit=50):
    """Zero Lag EC with a per-bar period series (alpha = 2/(period+1)), as in
    the "Adaptive Zero Lag EMA" strategies, which pass round() of a Cosine or
    I-Q IFM period. A na period gives na and restarts the recursion from 0."""
    return _zlec_nb(close, 2.0 / (period + 1.0), int(gain_limit))


# ---------------------------------------------------------------------------
# Butterworth low-pass filters
# ---------------------------------------------------------------------------

@njit(cache=True)
def _butter_nb(x, taps, gain, fb, seed_bars, zero_seed):
    """y = gain*sum(taps[j]*nz(x[j])) + sum(fb[j]*nz(y[j+1])).

    NaN input gives NaN. Unless ``zero_seed``, the first ``seed_bars`` valid
    bars output the input itself (Ehlers' ``If CurrentBar < n then Butter = Price``).
    """
    nt = taps.shape[0]
    nf = fb.shape[0]
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        cnt = 0
        for i in range(x.shape[0]):
            v = x[i, c]
            if np.isnan(v):
                continue
            cnt += 1
            if not zero_seed and cnt <= seed_bars:
                out[i, c] = v
                continue
            s = 0.0
            for j in range(nt):
                if i - j >= 0:
                    s += taps[j] * _nz(x[i - j, c])
            s *= gain
            for j in range(nf):
                if i - 1 - j >= 0:
                    s += fb[j] * _nz(out[i - 1 - j, c])
            out[i, c] = s
    return out


@indicator("BUTTERWORTH2", ["close"], ["butterworth"])
def ehlers_butterworth2(close, length=20, zero_seed=False):
    """Ehlers 2-pole Butterworth low-pass ("Cybernetic Analysis", 2004):
    a = exp(-sqrt2*pi/P), b = 2a*cos(sqrt2*pi/P);
    y = (1-b+a^2)/4*(x + 2x[1] + x[2]) + b*y[1] - a^2*y[2].

    Ehlers seeds the first two bars with the price; ``zero_seed=True`` gives the
    FMZ copies' ``nz()`` seeding bar for bar (they use exact sqrt(2), as here).
    """
    p = float(length)
    a1 = math.exp(-_SQRT2 * math.pi / p)
    b1 = 2 * a1 * math.cos(_SQRT2 * math.pi / p)
    return _butter_nb(close, np.array([1.0, 2.0, 1.0]), (1 - b1 + a1 * a1) / 4,
                      np.array([b1, -a1 * a1]), 2, bool(zero_seed))


@indicator("BUTTERWORTH3", ["close"], ["butterworth"])
def ehlers_butterworth3(close, length=20, method="ehlers"):
    """3-pole Butterworth low-pass, first three bars = price.

    method="ehlers": Ehlers' "Cybernetic Analysis" (2004) design, a = exp(-pi/P),
    b = 2a*cos(1.738*pi/P), c = a^2, gain (1-b+c)(1-c)/8 on x + 3x[1] + 3x[2] + x[3].
    method="bilinear": exact bilinear-transform Butterworth with prewarped
    cf = 2*tan(pi/P), as in the ``iirma`` copy (bar for bar, exact pi).
    """
    p = float(length)
    taps = np.array([1.0, 3.0, 3.0, 1.0])
    if str(method).lower() == "bilinear":
        cf = 2 * math.tan(math.pi / p)
        a0 = 8 + 8 * cf + 4 * cf ** 2 + cf ** 3
        a1 = -24 - 8 * cf + 4 * cf ** 2 + 3 * cf ** 3
        a2 = 24 - 8 * cf - 4 * cf ** 2 + 3 * cf ** 3
        a3 = -8 + 8 * cf - 4 * cf ** 2 + cf ** 3
        return _butter_nb(close, taps, cf ** 3 / a0, np.array([-a1 / a0, -a2 / a0, -a3 / a0]), 3, False)
    a = math.exp(-math.pi / p)
    b = 2 * a * math.cos(1.738 * math.pi / p)
    cc = a * a
    return _butter_nb(close, taps, (1 - b + cc) * (1 - cc) / 8,
                      np.array([b + cc, -(cc + b * cc), cc * cc]), 3, False)


# ---------------------------------------------------------------------------
# Optimal tracking filter
# ---------------------------------------------------------------------------

@njit(cache=True)
def _otf_nb(src, rng):
    out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        v1 = NAN
        v2 = NAN
        v3 = NAN
        lam = NAN
        for i in range(src.shape[0]):
            s = src[i, c]
            d = s - src[i - 1, c] if i >= 1 else NAN
            v1 = 0.2 * d + 0.8 * _nz(v1)
            v2 = 0.1 * rng[i, c] + 0.8 * _nz(v2)
            if not np.isnan(v2) and v2 != 0.0:
                lam = abs(v1 / v2)
            al = (-lam * lam + math.sqrt(lam ** 4 + 16 * lam * lam)) / 8
            v3 = al * s + (1 - al) * _nz(v3)
            out[i, c] = v3
    return out


@indicator("EHLERS_OPTIMAL_TRACKING", ["source", "high", "low", "close"], ["otf"])
def ehlers_optimal_tracking(source, high, low, close, true_range=False):
    """Ehlers Optimal Tracking Filter (Kalata tracking index): lambda =
    |ema(.2) of change| / ema(.1, .8) of range, alpha = (-l^2 + sqrt(l^4+16l^2))/8,
    out = alpha*src + (1-alpha)*out[1] (zero-seeded as in EasyLanguage).

    Ehlers' listing (ProRealCode copy) uses Price = hl2 and the H-L range; the
    FMZ copies filter a moving average and use ``ta.tr`` (``true_range=True``),
    bar for bar. ``close`` is only read for the true range.
    """
    if true_range:
        rng = k.tr_nb(high, low, close, False)
    else:
        rng = high - low
    return _otf_nb(source, rng)


# ---------------------------------------------------------------------------
# Roofing filter family
# ---------------------------------------------------------------------------

@njit(cache=True)
def _hp2_nb(x, a):
    out = np.full(x.shape, NAN)
    k1 = (1 - a / 2) * (1 - a / 2)
    for c in range(x.shape[1]):
        y1 = NAN
        y2 = NAN
        for i in range(x.shape[0]):
            v = NAN
            if i >= 2 and not np.isnan(x[i, c]) and not np.isnan(x[i - 1, c]) and not np.isnan(x[i - 2, c]):
                v = (k1 * (x[i, c] - 2 * x[i - 1, c] + x[i - 2, c])
                     + 2 * (1 - a) * _nz(y1) - (1 - a) * (1 - a) * _nz(y2))
            out[i, c] = v
            y2 = y1
            y1 = v
    return out


def _hp2_alpha(length):
    w = 0.707 * 2 * math.pi / length
    return (math.cos(w) + math.sin(w) - 1) / math.cos(w)


@indicator("EHLERS_HIGHPASS2", ["close"], ["hp"])
def ehlers_highpass2(close, length=48):
    """Ehlers 2-pole high-pass filter (Cycle Analytics, 2013; roofing filter
    stage): alpha = (cos(.707*360/P) + sin(.707*360/P) - 1)/cos(.707*360/P).
    na until close[2] exists. The Boom Hunter copy writes nz(close[1]), which
    injects a step of size close at bar 0 and a transient of several hundred bars.
    """
    return _hp2_nb(close, _hp2_alpha(float(length)))


@indicator("EHLERS_ROOFING", ["close"], ["roofing"])
def ehlers_roofing_filter(close, hp_length=48, ss_length=10):
    """Ehlers Roofing Filter (Cycle Analytics / TASC Jan 2014): 2-pole high-pass
    (``hp_length``) then the 1.414 Super Smoother (``ss_length``) on
    (hp + hp[1])/2. The Boom Hunter copy uses hp 100 and ss 6 / 28."""
    return _supersmoother_2d(_hp2_nb(close, _hp2_alpha(float(hp_length))), ss_length)


@njit(cache=True)
def _agc_nb(x, decay):
    xo = np.full(x.shape, NAN)
    po = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        peak = 0.0
        for i in range(x.shape[0]):
            v = x[i, c]
            peak = decay * peak
            if abs(v) > peak:
                peak = abs(v)
            if np.isnan(v):
                xo[i, c] = NAN
            else:
                xo[i, c] = v / peak if peak != 0 else 0.0
            po[i, c] = peak
    return xo, po


@indicator("EHLERS_AGC", ["close"], ["normalized", "peak"])
def ehlers_agc(close, decay=0.991):
    """Ehlers automatic gain control, fast attack / slow decay (TASC Aug 2014,
    "The Quotient Transform"; Cycle Analytics): peak = max(|x|, decay*peak[1]),
    normalized = x/peak in [-1, 1]. Feed it a roofing filter output."""
    return _agc_nb(close, float(decay))


# ---------------------------------------------------------------------------
# Oscillators
# ---------------------------------------------------------------------------

@njit(cache=True)
def _cyber_cycle_nb(x, alpha, alpha2):
    shape = x.shape
    cy = np.full(shape, NAN)
    sig = np.full(shape, NAN)
    k1 = (1 - 0.5 * alpha) * (1 - 0.5 * alpha)
    for c in range(shape[1]):
        sp = NAN
        for i in range(shape[0]):
            v = NAN
            if i < 6:
                if i >= 2:
                    v = (x[i, c] - 2 * x[i - 1, c] + x[i - 2, c]) / 4
            else:
                s0 = (x[i, c] + 2 * x[i - 1, c] + 2 * x[i - 2, c] + x[i - 3, c]) / 6
                s1 = (x[i - 1, c] + 2 * x[i - 2, c] + 2 * x[i - 3, c] + x[i - 4, c]) / 6
                s2 = (x[i - 2, c] + 2 * x[i - 3, c] + 2 * x[i - 4, c] + x[i - 5, c]) / 6
                v = (k1 * (s0 - 2 * s1 + s2) + 2 * (1 - alpha) * _nz(cy[i - 1, c])
                     - (1 - alpha) * (1 - alpha) * _nz(cy[i - 2, c]))
            cy[i, c] = v
            sp = alpha2 * v + (1 - alpha2) * _nz(sp)
            sig[i, c] = sp
    return cy, sig


@indicator("EHLERS_CYBER_CYCLE", ["close"], ["cycle", "trigger", "signal"])
def ehlers_cyber_cycle(close, alpha=0.07, signal_lag=9):
    """Ehlers Cyber Cycle ("Cybernetic Analysis", 2004, ch. 4): 2-pole high-pass
    of the 4-bar FIR smooth; first 6 bars use (p - 2p[1] + p[2])/4. ``trigger`` =
    cycle[1]. ``signal`` = the FMZ strategy's EMA(alpha 1/(lag+1)) of the cycle.
    Ehlers' price is hl2. The copy's ``na(cycle[7])`` test keeps the start-up
    formula 3 bars longer (warm-up only).
    """
    cy, sig = _cyber_cycle_nb(close, float(alpha), 1.0 / (signal_lag + 1.0))
    return cy, shift_2d(cy, 1), sig


@njit(cache=True)
def _ratio_hold_nb(cu, cd):
    out = np.full(cu.shape, NAN)
    for c in range(cu.shape[1]):
        prev = NAN
        for i in range(cu.shape[0]):
            u, d = cu[i, c], cd[i, c]
            if not np.isnan(u) and not np.isnan(d) and u + d != 0:
                prev = u / (u + d)
            elif np.isnan(u) or np.isnan(d):
                prev = NAN
            out[i, c] = prev
    return out


@indicator("EHLERS_SMOOTHED_RSI", ["close"], ["srsi"])
def ehlers_smoothed_rsi(close, length=10):
    """Ehlers Smoothed RSI ("Rocket Science for Traders", 2001): RSI-style
    CU/(CU+CD) over ``length`` changes of the (1,2,2,1)/6 smoothed close, 0..1.
    A zero-movement window keeps the previous value (HPotter's copy gives 0).
    """
    sm = (close + 2 * shift_2d(close, 1) + 2 * shift_2d(close, 2) + shift_2d(close, 3)) / 6
    d = sm - shift_2d(sm, 1)
    with np.errstate(invalid="ignore"):
        up = np.where(d > 0, d, np.where(np.isnan(d), NAN, 0.0))
        dn = np.where(d < 0, -d, np.where(np.isnan(d), NAN, 0.0))
    n = int(length)
    return _ratio_hold_nb(k.sum_nb(up, n), k.sum_nb(dn, n))


@njit(cache=True)
def _voss_nb(x, f1, s1, order):
    shape = x.shape
    vo = np.full(shape, NAN)
    fo = np.full(shape, NAN)
    for c in range(shape[1]):
        for i in range(shape[0]):
            if i <= 4:
                f = 0.0
            elif np.isnan(x[i, c]) or np.isnan(x[i - 2, c]):
                f = NAN
            else:
                f = (0.5 * (1 - s1) * (x[i, c] - x[i - 2, c]) + f1 * (1 + s1) * _nz(fo[i - 1, c])
                     - s1 * _nz(fo[i - 2, c]))
            sumc = 0.0
            for j in range(order):
                b = i - (order - j)
                if b >= 0:
                    sumc += (j + 1.0) / order * _nz(vo[b, c])
            fo[i, c] = f
            vo[i, c] = (3 + order) / 2.0 * f - sumc
    return vo, fo


@indicator("EHLERS_VOSS", ["close"], ["voss", "filt"])
def ehlers_voss(close, period=20, predict=3, bandwidth=0.25):
    """Ehlers Voss predictive filter (TASC Aug 2019, "A Peek Into The Future"):
    wide band-pass ``filt`` (zero for the first 5 bars) and the Voss predictor
    with order 3*predict. The FMZ copy zeroes both lines for the first 3*predict
    bars (warm-up only; the predictor's recursion is stable).
    """
    order = 3 * int(predict)
    f1 = math.cos(2 * math.pi / period)
    g1 = math.cos(bandwidth * 2 * math.pi / period)
    s1 = 1 / g1 - math.sqrt(1 / (g1 * g1) - 1)
    return _voss_nb(close, f1, s1, order)


@njit(cache=True)
def _lp1_nb(x, a):
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        y = NAN
        for i in range(x.shape[0]):
            v = x[i, c]
            if not np.isnan(v):
                p1 = _nz(x[i - 1, c]) if i > 0 else 0.0
                v = a / 2 * (v + p1) + (1 - a) * _nz(y)
            out[i, c] = v
            y = v
    return out


@indicator("EHLERS_DECYCLER", ["close"], ["decycler"])
def ehlers_decycler(close, length=60):
    """Ehlers Decycler ("Cycle Analytics for Traders", 2013, ch. 4): price minus
    a 1-pole high-pass, i.e. (a/2)*(x + x[1]) + (1-a)*y[1] with
    a = (cos(360/P) + sin(360/P) - 1)/cos(360/P). Bar for bar with the copy.
    (TASC Sep 2015's "Simple Decycler" is close - ehlers_highpass2(close, 125).)
    """
    w = 2 * math.pi / length
    return _lp1_nb(close, (math.cos(w) + math.sin(w) - 1) / math.cos(w))


@njit(cache=True)
def _stoch_hold_nb(x, hh, ll):
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        prev = NAN
        for i in range(x.shape[0]):
            r = hh[i, c] - ll[i, c]
            if np.isnan(r) or np.isnan(x[i, c]):
                prev = NAN
            elif r != 0:
                prev = (x[i, c] - ll[i, c]) / r
            out[i, c] = prev
    return out


@indicator("EHLERS_FISHER_STOCH", ["close"], ["fisher", "trigger"])
def ehlers_fisher_stoch(close, length=10, normalize=False):
    """Ehlers "Fisher Stochastic" of any series (Cybernetic Analysis, 2004:
    Fisher Stochastic CG / RVI / Cyber Cycle): stochastic over ``length``,
    (4,3,2,1)/10 WMA, then .5*ln((1+1.98(v-.5))/(1-1.98(v-.5))); trigger =
    fisher[1]. ``normalize`` divides by 2.64 as the FMZ RVI strategy does.
    A flat window keeps the previous stochastic (Pine's stoch gives na).
    """
    n = int(length)
    v1 = _stoch_hold_nb(close, k.highest_nb(close, n), k.lowest_nb(close, n))
    v2 = (4 * v1 + 3 * shift_2d(v1, 1) + 2 * shift_2d(v1, 2) + shift_2d(v1, 3)) / 10
    z = 1.98 * (v2 - 0.5)
    with np.errstate(invalid="ignore", divide="ignore"):
        f = 0.5 * np.log((1 + z) / (1 - z))
    if normalize:
        f = f / 2.64
    return f, shift_2d(f, 1)


@njit(cache=True)
def _flex_nb(filt, n, ms_alpha, reflex):
    out = np.full(filt.shape, NAN)
    for c in range(filt.shape[1]):
        ms = NAN
        for i in range(filt.shape[0]):
            s = NAN
            if i >= n:
                f0 = filt[i, c]
                slope = (filt[i - n, c] - f0) / n
                s = 0.0
                for j in range(1, n + 1):
                    s += (f0 + j * slope - filt[i - j, c]) if reflex else (f0 - filt[i - j, c])
                s /= n
            ms = ms_alpha * s * s + (1 - ms_alpha) * _nz(ms)
            if np.isnan(s):
                out[i, c] = NAN
            else:
                out[i, c] = s / math.sqrt(ms) if ms != 0 else 0.0
    return out


def _flex_2d(close, length, ss_length, ms_alpha, reflex):
    n = int(length)
    ssl = float(ss_length) if ss_length else 0.5 * n
    filt = _supersmoother_2d(close, ssl, _SQRT2)
    return _flex_nb(filt, n, float(ms_alpha), reflex)


@indicator("EHLERS_TRENDFLEX", ["close"], ["trendflex"])
def ehlers_trendflex(close, length=20, ss_length=0, ms_alpha=0.04):
    """Ehlers Trendflex (TASC Feb 2020, "Reflex: A New Zero-Lag Indicator"):
    mean of filt - filt[i], i=1..length, of a Super Smoother with period
    ``ss_length`` (0 = length/2, Ehlers), divided by sqrt of its .04 EMA of squares.

    The TFO copy is this with length 14, ss_length 8, ms_alpha 2/34 (its
    "EMA 33"). The Eltrut copy smooths with period = length and no 2-bar input
    average, so its curve is not Ehlers'.
    """
    return _flex_2d(close, length, ss_length, ms_alpha, False)


@indicator("EHLERS_REFLEX", ["close"], ["reflex"])
def ehlers_reflex(close, length=20, ss_length=0, ms_alpha=0.04):
    """Ehlers Reflex (TASC Feb 2020): like Trendflex but each difference is
    taken from the line joining filt and filt[length] (slope-corrected)."""
    return _flex_2d(close, length, ss_length, ms_alpha, True)


# ---------------------------------------------------------------------------
# HPotter indicators filed under "Ehlers"
# ---------------------------------------------------------------------------

@njit(cache=True)
def _sign_state_nb(x, ref):
    out = np.zeros(x.shape)
    for c in range(x.shape[1]):
        pos = 0.0
        for i in range(x.shape[0]):
            if x[i, c] > ref[i, c]:
                pos = 1.0
            elif x[i, c] < ref[i, c]:
                pos = -1.0
            out[i, c] = pos
    return out


@indicator("DELI", ["close"], ["dsp", "deli", "pos"])
def deli(close, length=7):
    """Detrended Ehlers Leading Indicator [HPotter] (after "MESA and Trading
    Market Cycles", pp. 64-70): DSP = ema(x, n) - ema(x, 2n), DELI = DSP -
    ema(DSP, n); ``pos`` = sign state. HPotter feeds daily hl2; pass that series
    yourself (resampled without look-ahead)."""
    n = int(length)
    dsp = k.ema_nb(close, n) - k.ema_nb(close, 2 * n)
    d = dsp - k.ema_nb(dsp, n)
    return dsp, d, _sign_state_nb(d, np.zeros(d.shape))


@indicator("ERGODIC_MDI", ["close"], ["ergodic", "signal", "pos"])
def ergodic_mdi(close, r=32, s=5, u=5, signal_length=5):
    """William Blau's Ergodic Mean Deviation Indicator, HPotter's port (not an
    Ehlers indicator): ema(ema(close - ema(close, r), s), u) and an EMA signal
    line; ``pos`` = 1/-1 on ergodic above/below signal. HPotter's signal uses
    ``u`` (his SmthLen input is unused), hence ``signal_length`` = 5."""
    mdi = close - k.ema_nb(close, int(r))
    erg = k.ema_nb(k.ema_nb(mdi, int(s)), int(u))
    sig = k.ema_nb(erg, int(signal_length))
    return erg, sig, _sign_state_nb(erg, sig)


# Keep these out of tv_indicators' registry so the main library is unchanged.
EXTRA_EHLERS = {name: REGISTRY.pop(name) for name in list(REGISTRY) if name not in _BEFORE}

__all__ = sorted(fn.__name__ for fn in EXTRA_EHLERS.values())
