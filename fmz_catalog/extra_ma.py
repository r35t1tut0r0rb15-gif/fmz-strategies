"""Staging area: moving averages, filters and kernel smoothers that FMZ
strategies use and ``tv_indicators`` / ``fmz_catalog.extra`` do not have.

Same conventions as ``fmz_catalog.extra``: each indicator is a numba/numpy
core registered with ``@indicator``; importing this module moves the entries
out of ``tv_indicators``' registry into ``EXTRA_MA``, so the main library and
its vectorbt classes are unchanged.

Pine semantics are kept on purpose: ``na`` comparisons are false, ``nz()``
seeds are reproduced where the original author wrote them, ``x[n]`` is ``na``
before bar ``n``, and window functions return ``na`` while their window holds
an ``na`` (the library-wide convention). Nothing looks ahead.

Where an indicator has a published original (Fries' eVWMA, LazyBear's VMA,
Duerschner's NMA, everget's Henderson / Sine WMA / EDSMA / RSX, LuxAlgo's
TRAMA, Ahrens, Satchwell, alexgrover's Uhl crossover...) the code follows
that original. Functions marked *strategy-specific* are an author's own
helper with no external definition; the strategy's code is the definition
and is ported line by line. Every docstring says which, and where a strategy
copy has a bug the docstring and ``scan/impl/ma_filters_report.json`` say
what it is.

    import fmz_catalog.extra_ma as xm
    ev = xm.evwma(df.close, df.volume, 20)
    cma, cts = xm.uhl_ma(df.close, 100)
"""

import math

import numpy as np
from numba import njit

from fmz_catalog.extra import _jma_nb
from tv_indicators import kernels as k
from tv_indicators._core import (REGISTRY, hma_2d, indicator, ma_2d, ma_kind, safe_div,
                                 shift_2d)
from tv_indicators.volatility import atr_2d

NAN = np.nan
_BEFORE = set(REGISTRY)


def _pround(x):
    """Pine ``math.round`` for non-negative numbers (half away from zero)."""
    return int(math.floor(x + 0.5))


# ---------------------------------------------------------------------------
# Shared kernels
# ---------------------------------------------------------------------------

@njit(cache=True)
def _fir_nb(x, w, norm):
    """sum_j x[i-j] * w[j] / norm, j = 0 is the current bar.

    Summed in the order the Pine loops use (current bar first). ``na`` in the
    window gives ``na`` (``na * 0`` is ``na`` in Pine too).
    """
    n = w.shape[0]
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for i in range(n - 1, x.shape[0]):
            s = 0.0
            for j in range(n):
                s += x[i - j, c] * w[j]
            out[i, c] = s / norm
    return out


def _fir(x, w):
    """Weighted window average with weights summed in loop order."""
    w = np.asarray(w, dtype=np.float64)
    tot = 0.0
    for v in w:
        tot += v
    return _fir_nb(x, w, tot)


def _ma(x, n, kind):
    """``ma_2d`` plus the Pine extras the scripts here pick by name."""
    kind = str(kind).strip().lower()
    if kind in ("none", "off", ""):
        return x.copy()
    if kind == "alma":
        return k.alma_nb(x, int(n), 0.85, 6.0, False)
    if kind == "swma":
        return (x + 2 * shift_2d(x, 1) + 2 * shift_2d(x, 2) + shift_2d(x, 3)) / 6
    return ma_2d(x, int(n), kind)


# ---------------------------------------------------------------------------
# Volume-weighted averages
# ---------------------------------------------------------------------------

@njit(cache=True)
def _evwma_nb(price, vol, nvol, seed_price):
    out = np.full(price.shape, NAN)
    for c in range(price.shape[1]):
        prev = NAN
        for i in range(price.shape[0]):
            p = price[i, c]
            v = vol[i, c]
            nn = nvol[i, c]
            if np.isnan(p) or np.isnan(v) or np.isnan(nn) or nn == 0:
                prev = NAN
                continue
            base = prev
            if np.isnan(base):
                base = p if seed_price else 0.0
            prev = ((nn - v) * base + v * p) / nn
            out[i, c] = prev
    return out


@indicator("EVWMA", ["close", "volume"], ["evwma"])
def evwma(close, volume, length=20, seed="close", cumulative=False):
    """Elastic Volume Weighted Moving Average (Christian P. Fries, 2001).

    eVWMA = ((N - v) * eVWMA[1] + v * price) / N, where Fries' N (the number
    of floating shares) is replaced by the sum of the last ``length``
    volumes, as in LazyBear's TradingView port; ``cumulative=True`` uses the
    cumulative volume instead (LazyBear's ``useCV``).

    ``seed="close"`` starts at the price (QuantNomad's EVWBB / EVWMA scripts,
    ``nz(evwma[1], close)``); ``seed="zero"`` reproduces LazyBear's
    ``nz(data[1])`` zero start, which only differs during the warm-up.
    """
    n = int(length)
    nvol = k.cum_nb(volume) if cumulative else k.sum_nb(volume, n)
    return _evwma_nb(close, volume, nvol, str(seed).lower() != "zero")


@indicator("VWEMA", ["close", "volume"], ["vwema"])
def vwema(close, volume, length=20):
    """Exponential volume-weighted MA: ``ema(src*volume, n) / ema(volume, n)``
    (strategy-specific helper ``vwma_e``; both EMAs are ``ta.ema``)."""
    n = int(length)
    return safe_div(k.ema_nb(close * volume, n), k.ema_nb(volume, n))


@njit(cache=True)
def _session_vwma_nb(src, vol, sess, length, include_open):
    out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        bs = NAN
        for i in range(src.shape[0]):
            if i > 0 and sess[i, c] != sess[i - 1, c] and not np.isnan(sess[i - 1, c]) \
                    and not np.isnan(sess[i, c]):
                bs = 0.0
            elif not np.isnan(bs):
                bs += 1.0
            if np.isnan(bs):
                n = length
            elif include_open:
                n = min(int(bs) + 1, length)
            else:
                n = max(1, int(bs) if bs < length else length)
            if i < n - 1:
                continue
            sp = 0.0
            sv = 0.0
            for j in range(n):
                sp += src[i - j, c] * vol[i - j, c]
                sv += vol[i - j, c]
            out[i, c] = (sp / n) / (sv / n) if sv != 0 else NAN
    return out


@indicator("SESSION_VWMA", ["close", "volume", "session"], ["vwma"])
def session_vwma(close, volume, session, length=55, include_session_open=True):
    """VWMA whose length is capped at the bars elapsed in the current session
    (strategy-specific ``day_vwma``, "SVWMA" strategies).

    ``session`` is a session id per bar (``tv_indicators.volume.session_ids``);
    a new session starts when it changes. The strategy computes
    ``max(1, barssince(newSession))`` bars, which leaves out the session's
    first bar (the window on its 3rd bar is 2 bars long). The default
    ``include_session_open=True`` counts that bar (window = barssince + 1);
    ``False`` reproduces the strategy. Before the first session change the
    full ``length`` is used, as in the script.
    """
    return _session_vwma_nb(close, volume, session, int(length), bool(include_session_open))


@njit(cache=True)
def _vawma_nb(src, vol, atr, length):
    out = np.full(src.shape, NAN)
    n = length
    for c in range(src.shape[1]):
        for i in range(n, src.shape[0]):
            sa = 0.0
            sv = 0.0
            for j in range(n):  # sma(atr, n), sma(volume, n) of the current bar
                sa += atr[i - j, c]
                sv += vol[i - j, c]
            aavg = sa / n
            vavg = sv / n
            ws = 0.0
            sw = 0.0
            for j in range(n + 1):  # the script loops 0..length (length + 1 bars)
                w = (vol[i - j, c] / vavg + atr[i - j, c] / aavg) / 2
                ws += src[i - j, c] * w
                sw += w
            out[i, c] = ws / sw
    return out


@indicator("VAWMA", ["close", "high", "low", "volume"], ["vawma"])
def vawma(close, high, low, volume, length=20):
    """Volume- and ATR-weighted MA from the VAWSI strategy (strategy-specific).

    weight[i] = (volume[i]/sma(volume, n) + tr[i]/sma(tr, n)) / 2, averaged
    over ``length + 1`` bars (the script's ``for i = 0 to length``). ``tr`` is
    ``ta.atr(1)`` = true range. The strategy feeds a per-bar dynamic length
    (Ehlers dominant cycle); this function takes a fixed length.
    """
    tr = k.tr_nb(high, low, close, True)
    return _vawma_nb(close, volume, tr, int(length))


# ---------------------------------------------------------------------------
# Slope angle
# ---------------------------------------------------------------------------

@indicator("MA_ANGLE_ATR", ["source", "high", "low", "close"], ["angle"])
def ma_angle_atr(source, high, low, close, lookback=1, atr_length=14, per_bar=False):
    """Slope angle in degrees: ``atan((src - src[lookback]) / atr) * 180/pi``.

    The common community formula (``angle()`` / ``f_angle()`` helpers) with
    ``ta.atr``. ``per_bar=True`` also divides by ``lookback`` as in the
    "Dual Moving Average" strategy's ``f_angle``. The scripts' 3.14159265359
    for pi changes the result by ~1e-13.
    """
    lb = int(lookback)
    atr = atr_2d(high, low, close, int(atr_length))
    ratio = safe_div(source - shift_2d(source, lb), atr)
    if per_bar:
        ratio = ratio / lb
    return np.degrees(np.arctan(ratio))


# ---------------------------------------------------------------------------
# Kalman (alpha-beta) smoother
# ---------------------------------------------------------------------------

@njit(cache=True)
def _kalman_nb(src, g, sq):
    kf = np.full(src.shape, NAN)
    vel = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        pk = NAN
        pv = NAN
        for i in range(src.shape[0]):
            x = src[i, c]
            if np.isnan(x):
                pk = NAN
                pv = NAN
                continue
            base = x if np.isnan(pk) else pk
            dk = x - base
            sm = base + dk * sq
            pv = (0.0 if np.isnan(pv) else pv) + g * dk
            pk = sm + pv
            kf[i, c] = pk
            vel[i, c] = pv
    return kf, vel


@indicator("KALMAN_AB", ["close"], ["kalman", "velocity"])
def kalman_alpha_beta(close, gain=0.7, scale=1.0, sharpness=2.0):
    """The TradingView community "Kalman" filter (Hull Suite / BRAHMASTRA
    ``kahlman()``, Loft Stop, "Kalman trend" scripts): a steady-state
    alpha-beta (g-h) tracker.

        g = gain / scale
        dk = src - kf[1]; kf = kf[1] + dk*sqrt(sharpness*g) + velo
        velo = velo[1] + g*dk

    seeded with the price (``nz(kf[1], src)``, ``nz(velo[1], 0)``).
    ``scale=1`` for ``kahlman(x, g)`` (gain 0.7 in BRAHMASTRA); ``scale=10000``
    for the ``gain / 10000`` versions; the "Transitive Ratio" strategy is
    ``gain=K, scale=100, sharpness=Sharpness``.
    """
    g = float(gain) / float(scale)
    return _kalman_nb(close, g, math.sqrt(float(sharpness) * g))


# ---------------------------------------------------------------------------
# SSL Hybrid baseline (Mihkel00) and its building blocks
# ---------------------------------------------------------------------------

@njit(cache=True)
def _modular_filter_nb(src, length, beta, feedback, z):
    out = np.full(src.shape, NAN)
    alpha = 2.0 / (length + 1)
    for c in range(src.shape[1]):
        ts = NAN
        b = NAN
        cc = NAN
        os = NAN
        for i in range(src.shape[0]):
            s = src[i, c]
            if feedback:
                a = z * s + (1 - z) * (s if np.isnan(ts) else ts)
            else:
                a = s
            e = alpha * a + (1 - alpha) * (a if np.isnan(b) else b)
            b = a if a > e else e
            e2 = alpha * a + (1 - alpha) * (a if np.isnan(cc) else cc)
            cc = a if a < e2 else e2
            if a == b:
                os = 1.0
            elif a == cc:
                os = 0.0
            upper = beta * b + (1 - beta) * cc
            lower = beta * cc + (1 - beta) * b
            ts = os * upper + (1 - os) * lower
            out[i, c] = ts
    return out


@njit(cache=True)
def _ssf_nb(x, length, poles):
    """everget's get2PoleSSF / get3PoleSSF: ``na`` input gives ``na``, the
    history is read with ``nz()``."""
    out = np.full(x.shape, NAN)
    pi = 2 * math.asin(1.0)
    if poles == 2:
        arg = math.sqrt(2.0) * pi / length
        a1 = math.exp(-arg)
        c2 = 2 * a1 * math.cos(arg)
        c3 = -(a1 ** 2)
        c4 = 0.0
        c1 = 1 - c2 - c3
    else:
        arg = pi / length
        a1 = math.exp(-arg)
        b1 = 2 * a1 * math.cos(1.738 * arg)
        cq = a1 ** 2
        c2 = b1 + cq
        c3 = -(cq + b1 * cq)
        c4 = cq ** 2
        c1 = 1 - c2 - c3 - c4
    for c in range(x.shape[1]):
        h1 = 0.0
        h2 = 0.0
        h3 = 0.0
        for i in range(x.shape[0]):
            v = c1 * x[i, c] + c2 * h1 + c3 * h2 + c4 * h3
            out[i, c] = v
            h3 = h2
            h2 = h1
            h1 = 0.0 if np.isnan(v) else v
    return out


@njit(cache=True)
def _edsma_nb(src, sd, ssf, length):
    out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        e = 0.0
        for i in range(src.shape[0]):
            s = sd[i, c]
            scaled = ssf[i, c] / s if s != 0 and not np.isnan(s) else 0.0
            al = 5 * abs(scaled) / length
            nv = al * src[i, c] + (1 - al) * e
            e = 0.0 if np.isnan(nv) else nv
            if not np.isnan(s):  # the script prints 0 until stdev exists
                out[i, c] = nv
    return out


def _edsma_2d(x, length, ssf_length, poles):
    zeros = x - np.nan_to_num(shift_2d(x, 2))
    avg = (zeros + shift_2d(zeros, 1)) / 2
    ssf = _ssf_nb(avg, float(ssf_length), int(poles))
    return _edsma_nb(x, k.stdev_nb(ssf, int(length)), ssf, float(length))


@indicator("EDSMA", ["close"], ["edsma"])
def edsma(close, length=40, ssf_length=20, poles=2):
    """Ehlers Deviation-Scaled Moving Average [everget].

    Super Smoother (2 or 3 poles, everget's ``get2PoleSSF``/``get3PoleSSF``)
    of the 2-bar momentum average, scaled by its ``stdev(length)``;
    alpha = 5*|scaled|/length; EDSMA = alpha*src + (1-alpha)*EDSMA[1] from 0.
    The script prints 0 while the stdev is ``na``; here those bars are ``na``
    and the recursion starts from 0 afterwards, so the values are the same.
    """
    return _edsma_2d(close, int(length), int(ssf_length), int(poles))


_SSL_TYPES = ("SMA", "EMA", "DEMA", "TEMA", "LSMA", "WMA", "MF", "VAMA", "TMA", "HMA",
              "JMA", "KIJUN V2", "EDSMA", "MCGINLEY")


@indicator("SSL_HYBRID_MA", ["close", "high", "low"], ["ma"])
def ssl_hybrid_ma(close, high, low, length=60, ma_type="HMA", kidiv=1, jurik_phase=3,
                  jurik_power=1, volatility_lookback=10, mf_beta=0.8, mf_feedback=False,
                  mf_z=0.5, ssf_length=20, ssf_poles=2):
    """The ``ma(type, src, len)`` selector of SSL Hybrid [Mihkel00].

    ``close`` is the source; ``high``/``low`` are only read by "Kijun v2",
    which (as in the script) uses ``ta.highest(high)``/``ta.lowest(low)``.
    Types: SMA, EMA, DEMA, TEMA, LSMA, WMA, MF (alexgrover's Modular
    Filter), VAMA (Joris Duyck's volatility-adjusted MA), TMA, HMA, JMA
    (everget), Kijun v2, EDSMA (everget), McGinley (TV built-in).
    """
    n = int(length)
    t = str(ma_type).strip().upper()
    if t not in _SSL_TYPES:
        raise ValueError(f"unknown ma_type {ma_type!r}; use one of {_SSL_TYPES}")
    if t in ("SMA", "EMA", "DEMA", "TEMA", "LSMA", "WMA", "HMA"):
        return ma_2d(close, n, t.lower())
    if t == "TMA":
        return k.sma_nb(k.sma_nb(close, int(math.ceil(n / 2))), int(math.floor(n / 2)) + 1)
    if t == "MF":
        return _modular_filter_nb(close, float(n), float(mf_beta), bool(mf_feedback), float(mf_z))
    if t == "VAMA":
        mid = k.ema_nb(close, n)
        dev = close - mid
        lb = int(volatility_lookback)
        return mid + (k.highest_nb(dev, lb) + k.lowest_nb(dev, lb)) / 2
    if t == "JMA":
        return _jma_nb(close, float(n), float(jurik_phase), float(jurik_power))
    if t == "KIJUN V2":
        m = max(int(n / kidiv), 1)
        kijun = (k.lowest_nb(low, n) + k.highest_nb(high, n)) / 2
        conv = (k.lowest_nb(low, m) + k.highest_nb(high, m)) / 2
        return (kijun + conv) / 2
    if t == "MCGINLEY":
        return k.mcginley_nb(close, k.ema_nb(close, n), float(n))
    return _edsma_2d(close, n, int(ssf_length), int(ssf_poles))


# ---------------------------------------------------------------------------
# Fixed-weight window averages
# ---------------------------------------------------------------------------

@njit(cache=True)
def _fir_nz_nb(x, w, norm):
    """Like ``_fir_nb`` but with ``nz(src[i])`` from bar 0 (script warm-up)."""
    n = w.shape[0]
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for i in range(x.shape[0]):
            s = 0.0
            for j in range(n):
                v = x[i - j, c] if i - j >= 0 else 0.0
                s += (0.0 if np.isnan(v) else v) * w[j]
            out[i, c] = s / norm
    return out


@indicator("SINE_WMA", ["close"], ["swma"])
def sine_wma(close, length=14, insilico_compat=False):
    """Sine-Weighted Moving Average [everget]: weight sin((i+1)*pi/(n+1)) for
    the bar i bars back (a half sine over the window, peak in the middle).

    ``insilico_compat=True`` reproduces the copy in "MA Emperor insiliconot"
    (``sin(i*pi/(n+1))``, so the current bar gets weight 0 and the window is
    effectively n-1 bars, with ``nz(src[i])`` zeros during warm-up). That is
    a bug; the default is everget's (and pandas-ta's) definition.
    """
    n = int(length)
    pi = 2 * math.asin(1.0)
    if insilico_compat:
        w = np.array([math.sin(i * pi / (n + 1)) for i in range(n)])
        tot = 0.0
        for v in w:
            tot += v
        return _fir_nz_nb(close, w, tot)
    return _fir(close, [math.sin((i + 1) * pi / (n + 1)) for i in range(n)])


def _henderson_weights(n):
    m = (n - 1) / 2
    w = []
    for i in range(n):
        j = i - m
        num = 315 * ((m + 1) ** 2 - j ** 2) * ((m + 2) ** 2 - j ** 2) * ((m + 3) ** 2 - j ** 2) \
            * (3 * (m + 2) ** 2 - 11 * j ** 2 - 16)
        den = 8 * (m + 2) * ((m + 2) ** 2 - 1) * (4 * (m + 2) ** 2 - 1) * (4 * (m + 2) ** 2 - 9) \
            * (4 * (m + 2) ** 2 - 25)
        w.append(num / den if den != 0 else 0.0)
    return w


@indicator("HENDERSON_MA", ["close"], ["hwma"])
def henderson_ma(close, length=7):
    """Henderson Weighted Moving Average [everget]: the (2m+1)-term Henderson
    weights, applied to the last ``length`` bars (trailing, no look-ahead).

    The weights are symmetric, so the trailing filter lags (length-1)/2 bars.
    The scripts use ``nz(src[i])`` during warm-up; here the first
    ``length-1`` bars are ``na``.
    """
    return _fir(close, _henderson_weights(int(length)))


@indicator("RETRO_WMA", ["close"], ["rwma"])
def retro_wma(close, length=20):
    """"Retro weighted MA" (strategy-specific, RSI Trend Following
    strategies): the newest 4 bars weigh x, older bars 1.3x, with
    x = 100/(4 + (n-4)*1.3)."""
    n = int(length)
    wx = 100 / (4 + (n - 4) * 1.30)
    wy = 1.30 * wx
    return _fir(close, [wx if i <= 3 else wy for i in range(n)])


@indicator("QUADRATIC_WMA", ["close"], ["qwma"])
def quadratic_wma(close, length=20):
    """WMA with weights (n - i)^2 (strategy-specific ``wma()`` of the "MACD and
    RSI Natural" strategy)."""
    n = int(length)
    return _fir(close, [float((n - i) * (n - i)) for i in range(n)])


@indicator("BINOMIAL_MA", ["close"], ["bma"])
def binomial_ma(close, length=10):
    """Binomial Moving Average [HosseinDaftary]: weights C(2n-1, n-1-i) for
    the bar i back (the upper half of the binomial row), normalised.

    The script computes factorials in Pine ``int``; 21! overflows int64, so on
    TradingView lengths >= 11 (the strategy's slow 30) give garbage weights.
    Here the coefficients are exact.
    """
    n = int(length)
    w = [float(math.comb(2 * n - 1, n - 1 - i)) for i in range(n)]
    tot = sum(w)
    return _fir_nb(close, np.array([v / tot for v in w]), 1.0)


@indicator("WINDOWED_EMA", ["close"], ["wema"])
def windowed_ema(close, length=20, decay=NAN):
    """EMA weights truncated to ``length`` bars and renormalised:
    sum(d^i * src[i]) / sum(d^i).

    ``decay`` defaults to 1 - 2/(length+1) (``adaptivePricePosition`` of the
    "Dual Exponential Smoothing" strategy); the EMA-200 strategy's helper
    (misnamed "Jurik") is ``decay=0.5``.
    """
    n = int(length)
    d = 1 - 2.0 / (n + 1) if np.isnan(decay) else float(decay)
    return _fir(close, [math.pow(d, i) for i in range(n)])


@indicator("GEOMETRIC_MEAN_MA", ["close"], ["gmean"])
def geometric_mean_ma(close, length=20):
    """Rolling geometric mean, prod(src[i]^(1/n)) (MA Emperor's
    ``variant_geoMean``). The script returns the price until bar_index > n;
    here the first n-1 bars are ``na``. Non-positive prices give ``na``."""
    n = int(length)
    with np.errstate(invalid="ignore", divide="ignore"):
        lg = np.where(close > 0, np.log(close), NAN)
    return np.exp(k.sum_nb(lg, n) / n)


@njit(cache=True)
def _signed_wma_nb(x, open_, close, n):
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for i in range(n - 1, x.shape[0]):
            s = 0.0
            nrm = 0.0
            for j in range(n):
                w = float((n - j) * n)
                nrm += w
                f = -1.0 if close[i - j, c] < open_[i - j, c] else 1.0
                s += x[i - j, c] * w * f
            out[i, c] = s / nrm
    return out


@indicator("SIGNED_WMA", ["source", "open", "close"], ["swma"])
def signed_wma(source, open, close, length=5):
    """Linear WMA whose terms are negated on down candles (close < open):
    ``pine_wma`` of the "Volume Divergence by MM" script (strategy-specific,
    applied there to volume)."""
    return _signed_wma_nb(source, open, close, int(length))


# ---------------------------------------------------------------------------
# Kernel smoothers
# ---------------------------------------------------------------------------

def _kernel_weights(n, kernel, alpha, beta, bandwidth):
    kernel = str(kernel).strip().lower()
    w = []
    for i in range(n):
        x = i / (n - 1)
        if kernel == "beta":
            with np.errstate(divide="ignore"):
                v = float(np.power(x, alpha - 1) * np.power(1 - x, beta - 1))
        elif kernel == "gaussian":
            v = math.exp(-0.5 * ((x - 0.5) / bandwidth) ** 2)
        elif kernel == "epanechnikov":
            v = max(0.0, 1 - ((x - 0.5) / bandwidth) ** 2)
        else:
            raise ValueError("kernel must be 'beta', 'gaussian' or 'epanechnikov'")
        w.append(v)
    tot = 0.0
    for v in w:
        tot += v
    return np.array([v / tot for v in w])


@indicator("KERNEL_MA", ["close"], ["kma"])
def kernel_ma(close, length=20, kernel="beta", alpha=3.0, beta=3.0, bandwidth=0.3):
    """Kernel-weighted MA of the "B4100 NW Trend Ribbon" strategy
    (strategy-specific). Weights over x = i/(n-1), i bars back:

    * beta: x^(alpha-1) * (1-x)^(beta-1)
    * gaussian: exp(-0.5*((x-0.5)/bandwidth)^2)
    * epanechnikov: max(0, 1 - ((x-0.5)/bandwidth)^2)

    normalised to sum 1. All three are zero or symmetric around the window
    middle, so with the defaults the current bar has weight 0 (beta) or the
    average lags about n/2 bars; that is the author's design.
    """
    return _fir_nb(close, _kernel_weights(int(length), kernel, float(alpha), float(beta),
                                          float(bandwidth)), 1.0)


def _nw_weights(n, bw, kind):
    w = []
    for i in range(n):
        r = i / bw
        if kind == "gauss":
            w.append(math.exp(-0.5 * r ** 2))
        else:
            w.append(1 - r ** 2 if abs(r) <= 1 else 0.0)
    tot = 0.0
    for v in w:
        tot += v
    return np.array(w), (tot if tot != 0 else 1.0)


@indicator("MULTI_KERNEL_REGRESSION", ["close"], ["mkr", "gaussian", "epanechnikov"])
def multi_kernel_regression(close, length=30, h_gaussian=5.0, h_epanechnikov=5.0,
                            gaussian_weight=0.5):
    """One-sided (no look-ahead) Nadaraya-Watson kernel regression of the
    "DR + Multi Kernel Regression" strategies (strategy-specific).

    gaussian w_i = exp(-0.5*(i/h)^2), epanechnikov w_i = 1-(i/h)^2 for
    |i/h| <= 1, over the last ``length`` bars; mkr is their mix.
    """
    n = int(length)
    wg, ng = _nw_weights(n, float(h_gaussian), "gauss")
    we, ne = _nw_weights(n, float(h_epanechnikov), "epan")
    g = _fir_nb(close, wg, ng)
    e = _fir_nb(close, we, ne)
    a = float(gaussian_weight)
    return a * g + (1 - a) * e, g, e


def _cp_gauss_weights(size, h, r):
    w = []
    for i in range(int(size) + 1):
        kk = i ** 2 / (h ** 2 * r)
        w.append(math.exp(-((kk / r) ** 2) / 2) / math.sqrt(2 * math.pi))
    return w


@indicator("KERNEL_REGRESSION_CP", ["close"], ["kernel"])
def kernel_regression_chartprime(close, size=64, h=4.0, r=0.5):
    """``gaussian_kernel(source, size, h, r)`` of ChartPrime's Ichimoku
    Oscillator (strategy-specific): weights exp(-(k/r)^2/2) with
    k = i^2/(h^2*r) over ``size + 1`` past bars, normalised."""
    return _fir(close, _cp_gauss_weights(size, float(h), float(r)))


@njit(cache=True)
def _cheby_nb(src, cc):
    out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        prev = 0.0
        for i in range(src.shape[0]):
            v = (1 - cc) * src[i, c] + cc * prev
            out[i, c] = v
            prev = 0.0 if np.isnan(v) else v
    return out


def _cheby_coef(length, ripple):
    def cosh(x):
        return (math.exp(x) + math.exp(-x)) / 2

    def sinh(x):
        return (math.exp(x) - math.exp(-x)) / 2

    x = 1 / (1 - ripple)
    acosh = math.log(x + math.sqrt(x * x - 1))
    y = 1 / ripple
    asinh = math.log(y + math.sqrt(y * y + 1))
    a = cosh(1 / length * acosh)
    b = sinh(1 / length * asinh)
    return (a - b) / (a + b)


@indicator("CHEBYSHEV_MA", ["close"], ["chebyshev"])
def chebyshev_ma(close, length=8.0, ripple=0.05):
    """"Chebyshev Type I Moving Average" of ChartPrime's Ichimoku Oscillator.

    Despite the name it is a one-pole exponential smoother:
    c = (a-b)/(a+b), a = cosh(acosh(1/(1-ripple))/len),
    b = sinh(asinh(1/ripple)/len); y = (1-c)*src + c*nz(y[1]) (zero seed, as
    published). ``ripple`` must be in (0, 1).
    """
    return _cheby_nb(close, _cheby_coef(float(length), float(ripple)))


@indicator("CHEBYSHEV_FILTER", ["close"], ["filter"])
def chebyshev_filter(close, length=3.0, extra=True):
    """ChartPrime Ichimoku Oscillator ``smoothing()``: ``chebyshevI(src, len,
    0.5)``, then (``extra=True``) ``gaussian_kernel(.., 4, 2, 1)``."""
    y = _cheby_nb(close, _cheby_coef(float(length), 0.5))
    if extra:
        y = _fir(y, _cp_gauss_weights(4, 2.0, 1.0))
    return y


@indicator("SINE_FIR", ["close"], ["filter"])
def sine_fir_filter(close, length=50, alpha=1.0, beta=0.5):
    """FIR filter with kernel sin(2*pi*x^alpha)*(1 - x^beta), x = i/(n-1),
    normalised by the weight sum: the "AMA" of LuxAlgo's alternating
    extremities script as copied in Kaspricci's "Crazy Scalping" strategy.
    ``alpha`` controls lag, ``beta`` overshoot. Uses the script's 3.14159.
    """
    n = int(length)
    w = []
    for i in range(n):
        x = i / (n - 1)
        w.append(math.sin(2 * 3.14159 * math.pow(x, alpha)) * (1 - math.pow(x, beta)))
    return _fir(close, w)


def _gauss_fir_w(n):
    half = (n - 1) / 2.0
    den = (n / 6.0) * (n / 6.0)
    return np.array([math.exp(-((i - half) * (i - half)) / (2 * den)) for i in range(n)])


@njit(cache=True)
def _wstd_nb(x, mid, w):
    n = w.shape[0]
    out = np.full(x.shape, NAN)
    tot = 0.0
    for j in range(n):
        tot += w[j]
    for c in range(x.shape[1]):
        for i in range(n - 1, x.shape[0]):
            s = 0.0
            for j in range(n):
                d = x[i - j, c] - mid[i, c]
                s += d * d * w[j]
            out[i, c] = math.sqrt(s / tot)
    return out


@indicator("GAUSSIAN_FIR", ["close"], ["mid", "std"])
def gaussian_fir(close, length=20):
    """Gaussian-weighted window average and stdev (strategy-specific
    ``f_gaussian`` / ``f_gaussian_std``): Gaussian centred on the middle of
    the last ``length`` bars with sigma = length/6. Trailing, so it lags
    about (length-1)/2 bars."""
    n = int(length)
    w = _gauss_fir_w(n)
    mid = _fir(close, w)
    return mid, _wstd_nb(close, mid, w)


# ---------------------------------------------------------------------------
# Adaptive averages
# ---------------------------------------------------------------------------

@njit(cache=True)
def _vma_nb(src, n, seed_sma, sma):
    out = np.full(src.shape, NAN)
    kk = 1.0 / n
    rows = src.shape[0]
    for c in range(src.shape[1]):
        i_s = np.full(rows, NAN)
        pdms = mdms = pdis = mdis = iss = NAN
        vma = NAN
        for i in range(rows):
            s = src[i, c]
            p1 = src[i - 1, c] if i > 0 else NAN
            ch = s - p1
            pdm = NAN if np.isnan(ch) else max(ch, 0.0)
            mdm = NAN if np.isnan(ch) else max(-ch, 0.0)
            pdms = (1 - kk) * (0.0 if np.isnan(pdms) else pdms) + kk * pdm
            mdms = (1 - kk) * (0.0 if np.isnan(mdms) else mdms) + kk * mdm
            ss = pdms + mdms
            pdi = pdms / ss if ss != 0 else NAN
            mdi = mdms / ss if ss != 0 else NAN
            pdis = (1 - kk) * (0.0 if np.isnan(pdis) else pdis) + kk * pdi
            mdis = (1 - kk) * (0.0 if np.isnan(mdis) else mdis) + kk * mdi
            d = abs(pdis - mdis)
            s1 = pdis + mdis
            iss = (1 - kk) * (0.0 if np.isnan(iss) else iss) + (kk * d / s1 if s1 != 0 else NAN)
            i_s[i] = iss
            vi = NAN
            if i >= n - 1:
                hh = -np.inf
                ll = np.inf
                ok = True
                for j in range(n):
                    v = i_s[i - j]
                    if np.isnan(v):
                        ok = False
                        break
                    hh = max(hh, v)
                    ll = min(ll, v)
                if ok and hh != ll:
                    vi = (iss - ll) / (hh - ll)
            if seed_sma and np.isnan(vma):
                vma = sma[i, c]
            elif np.isnan(vi):
                if not seed_sma and np.isnan(vma):
                    vma = NAN
                # flat iS window or na source: keep the previous value
            else:
                vma = kk * vi * s + (1 - kk * vi) * (0.0 if np.isnan(vma) else vma)
            out[i, c] = vma
    return out


@indicator("VMA_LB", ["close"], ["vma"])
def vma_lazybear(close, length=6, seed="zero"):
    """Variable Moving Average [LazyBear] (Chande's VIDYA idea driven by a
    DMI-like volatility index).

    pdm/mdm are the up/down moves, smoothed with alpha 1/length into pdi/mdi
    and their normalised spread iS; vi = (iS - lowest(iS))/(highest - lowest)
    over ``length``; VMA = k*vi*src + (1 - k*vi)*VMA[1], k = 1/length.

    ``seed="zero"`` is LazyBear's ``nz(vma[1])``; ``seed="sma"`` starts at
    ``ta.sma(src, length)`` like the "Multi-Trend Crossover" copy. Where the
    script gets ``na`` (iS flat over the whole window, so highest == lowest)
    its ``nz()`` restarts the average at 0; here the previous value is kept.
    """
    n = int(length)
    return _vma_nb(close, n, str(seed).lower() == "sma", k.sma_nb(close, n))


@njit(cache=True)
def _trama_nb(src, tc):
    out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        ama = NAN
        for i in range(src.shape[0]):
            v = ama + tc[i, c] * (src[i, c] - ama)
            ama = src[i, c] if np.isnan(v) else v
            out[i, c] = ama
    return out


@indicator("TRAMA", ["high", "low", "close"], ["trama"])
def trama(high, low, close, length=99):
    """Trend Regularity Adaptive Moving Average [LuxAlgo].

    tc = sma(new highest(high) or new lowest(low) ? 1 : 0, length)^2;
    ama = nz(ama[1] + tc*(src - ama[1]), src). The strategy copies are exact.
    """
    n = int(length)
    with np.errstate(invalid="ignore"):
        hh = np.sign(np.diff(k.highest_nb(high, n), axis=0, prepend=NAN)) > 0
        ll = np.sign(np.diff(k.lowest_nb(low, n), axis=0, prepend=NAN)) < 0
    tc = k.sma_nb((hh | ll).astype(np.float64), n) ** 2
    return _trama_nb(close, tc)


@njit(cache=True)
def _sama_nb(src, hh, ll, min_a, maj_a):
    out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        prev = 0.0
        for i in range(src.shape[0]):
            s = src[i, c]
            rng = hh[i, c] - ll[i, c]
            mult = abs(2 * s - ll[i, c] - hh[i, c]) / rng if (rng != 0 and not np.isnan(rng)) else 0.0
            fa = (mult * (min_a - maj_a) + maj_a) ** 2
            v = (s - prev) * fa + prev
            out[i, c] = v
            prev = 0.0 if np.isnan(v) else v
    return out


@indicator("SAMA", ["high", "low", "close"], ["sama"])
def slope_adaptive_ma(high, low, close, length=200, min_length=6, maj_length=14):
    """Slope Adaptive Moving Average [MightyZinger] (MZ SAMA ``ama()``).

    mult = |2*src - ll - hh|/(hh - ll) over highest(high)/lowest(low) of
    ``length+1`` bars; alpha = (mult*(a_min - a_maj) + a_maj)^2 with
    a = 2/(len+1). Starts from 0 (``nz(_ama[1])``) on the first bar, as
    published, so give it a few hundred bars of history.
    """
    n = int(length) + 1
    return _sama_nb(close, k.highest_nb(high, n), k.lowest_nb(low, n),
                    2.0 / (min_length + 1), 2.0 / (maj_length + 1))


@njit(cache=True)
def _uhl_nb(src, var, sma):
    cma_o = np.full(src.shape, NAN)
    cts_o = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        cma = NAN
        cts = NAN
        for i in range(src.shape[0]):
            s = src[i, c]
            vv = var[i, c]
            sm = sma[i, c]
            e1 = sm - cma
            secma = 0.0 if np.isnan(e1) else e1 * e1
            e2 = s - cts
            sects = 0.0 if np.isnan(e2) else e2 * e2
            ka = 1 - vv / secma if vv < secma else 0.0
            kb = 1 - vv / sects if vv < sects else 0.0
            cma = ka * sm + (1 - ka) * (s if np.isnan(cma) else cma)
            cts = kb * s + (1 - kb) * (s if np.isnan(cts) else cts)
            cma_o[i, c] = cma
            cts_o[i, c] = cts
    return cma_o, cts_o


@njit(cache=True)
def _variance_nb(x, n):
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for i in range(n - 1, x.shape[0]):
            m = 0.0
            for j in range(n):
                m += x[i - j, c]
            m /= n
            ss = 0.0
            for j in range(n):
                d = x[i - j, c] - m
                ss += d * d
            out[i, c] = ss / n
    return out


@indicator("UHL_MA", ["close"], ["cma", "cts"])
def uhl_ma(close, length=100, mult=1.0):
    """Andreas Uhl's corrected moving average and alexgrover's "Uhl MA
    Crossover System".

    cma (Uhl's corrected average): K = 1 - var/(sma - cma[1])^2 when that is
    positive, else 0; cma = K*sma + (1-K)*cma[1]. cts applies the same
    correction to the price itself. ``var`` = ``ta.variance`` (population)
    x ``mult``. Seeds are the price (``nz(cma[1], src)``); before the variance
    exists cts holds the first price, as in the script.
    """
    n = int(length)
    return _uhl_nb(close, _variance_nb(close, n) * float(mult), k.sma_nb(close, n))


@njit(cache=True)
def _wma_at(x, i, n):
    """WMA of the 1D buffer ``x`` ending at ``i`` (na if not enough bars)."""
    if i < n - 1:
        return NAN
    s = 0.0
    for j in range(n):
        s += x[i - j] * (n - j)
    return s / (n * (n + 1) / 2.0)


@njit(cache=True)
def _ama_durenard_nb(price, n, fast, lam, beta, snrf):
    shape = price.shape
    ama_o = np.full(shape, NAN)
    hb_o = np.full(shape, NAN)
    lb_o = np.full(shape, NAN)
    al = lam * (n - 1) / (n - lam)
    pi2 = 1.5707963267948966
    rows = shape[0]
    for c in range(shape[1]):
        xs = np.full(rows, NAN)
        w1 = np.full(rows, NAN)
        alpha = NAN   # alpha of the previous bar
        ama = NAN
        dmax = NAN
        dmin = NAN
        bhb = NAN
        blb = NAN
        for i in range(rows):
            p = price[i, c]
            pp = price[i - 1, c] if i > 0 else NAN
            ama_prev = ama
            ama = alpha * p + (1 - alpha) * (0.0 if np.isnan(ama_prev) else ama_prev)
            ret = (p - pp) / pp if pp != 0 else NAN
            up = NAN if np.isnan(ret) else max(ret, 0.0)
            dn = NAN if np.isnan(ret) else min(ret, 0.0)
            dmax = alpha * up + (1 - alpha) * (0.0 if np.isnan(dmax) else dmax)
            dmin = -alpha * dn + (1 - alpha) * (0.0 if np.isnan(dmin) else dmin)
            hb = (1 + bhb) * ama
            lb = (1 - blb) * ama
            bhb = beta * dmax
            blb = beta * dmin
            r = (p - ama_prev) / ama_prev if ama_prev != 0 else NAN
            if p > hb:
                snr = r / blb if blb != 0 else NAN
            elif p < lb:
                snr = -r / bhb if bhb != 0 else NAN
            else:
                snr = 0.0
            xs[i] = (math.atan(snrf * snr) + pi2) / (2 * pi2)
            w1[i] = _wma_at(xs, i, n)
            alpha = (1 + al) * w1[i] - al * _wma_at(w1, i, fast)
            ama_o[i, c] = ama
            hb_o[i, c] = hb
            lb_o[i, c] = lb
    return ama_o, hb_o, lb_o


@indicator("AMA_DURENARD", ["close"], ["ama", "upper", "lower"])
def ama_durenard(close, lookback=5, beta=2.1, snr_factor=2.1):
    """Adaptive MA channel from E. Durenard, "Professional Automated Trading"
    (2013), as coded by CryptoStatistical ("[CS] AMA Strategy - Channel Break
    Out"); strategy-specific port.

    ama = alpha[1]*price + (1-alpha[1])*ama[1]; the bands are
    ama*(1 +/- beta*smoothed up/down returns); the signal-to-noise of a
    breakout, squashed with atan to 0..1, is smoothed with Duerschner's NWMA
    (see ``nma_durschner``) to give the next alpha. Note that the NWMA can
    overshoot, so alpha is not confined to 0..1. Zero-seeded (``nz``).
    """
    n = int(lookback)
    fast = max(n // 2, 1)
    return _ama_durenard_nb(close, n, fast, 2.0, float(beta), float(snr_factor))


@njit(cache=True)
def _ma_conv_nb(src, upper, lower, init, length, kk, fast):
    shape = src.shape
    ma_o = np.full(shape, NAN)
    fma_o = np.full(shape, NAN)
    a0 = 2.0 / (length + 1)
    for c in range(shape[1]):
        ma = NAN
        alpha = 0.0          # var alpha = 0.
        alpha_hist = NAN     # alpha[1] (na before bar 0)
        fma = NAN
        b_prev = NAN         # the `ma` value ta.cross saw on the previous bar
        s_prev = NAN
        for i in range(shape[0]):
            s = src[i, c]
            b = 0.0 if i == 0 else ma   # var ma = 0. before its first update
            cross = (s > b and s_prev <= b_prev) or (s < b and s_prev >= b_prev)
            up_new = upper[i, c] > upper[i - 1, c] if i > 0 else False
            lo_new = lower[i, c] < lower[i - 1, c] if i > 0 else False
            if cross:
                alpha = a0
            elif s > b and up_new:
                alpha = alpha + kk
            elif s < b and lo_new:
                alpha = alpha + kk
            v = ma + alpha_hist * (s - ma)
            ma = init[i, c] if np.isnan(v) else v
            if cross:
                f = (s + fma) / 2
            elif s > ma:
                f = (NAN if np.isnan(fma) else max(s, fma)) + (s - fma) / fast
            else:
                f = (NAN if np.isnan(fma) else min(s, fma)) + (s - fma) / fast
            fma = s if np.isnan(f) else f
            alpha_hist = alpha
            b_prev = b
            s_prev = s
            ma_o[i, c] = ma
            fma_o[i, c] = fma
    return ma_o, fma_o


@indicator("MA_CONVERGING", ["high", "low", "close"], ["ma", "fma"])
def ma_converging(high, low, close, length=100, incr=10, fast=10):
    """MA Converging [LuxAlgo] (the "Dual MA Momentum Breakout" strategy).

    Starts at ``sma(src, length)``; its alpha resets to 2/(length+1) when the
    price crosses it and grows by 1/incr on every new ``length``-bar
    high (price above) or low (price below), so the average accelerates
    towards the price in a trend. ``ma`` uses ``alpha[1]``. ``fma`` is the
    fast line. Bar-for-bar with the script, including how ``ta.cross``
    sees the not-yet-updated ``var ma``.
    """
    n = int(length)
    return _ma_conv_nb(close, k.highest_nb(high, n), k.lowest_nb(low, n),
                       k.sma_nb(close, n), float(n), 1.0 / float(incr), float(fast))


# ---------------------------------------------------------------------------
# Durschner NMA and the OBV MACD [RafaelZioni] averages
# ---------------------------------------------------------------------------

def _nma(x, n, n2, lam, kind):
    if n == lam:
        return np.full(x.shape, NAN)
    al = lam * (n - 1) / (n - lam)
    m1 = ma_2d(x, n, kind)
    m2 = ma_2d(m1, max(int(n2), 1), kind)
    return (1 + al) * m1 - al * m2


@indicator("NMA_DURSCHNER", ["close"], ["nma"])
def nma_durschner(close, length=20, length2=0, ma_type="wma"):
    """Moving Average 3.0 (M. G. Duerschner, "Gleitende Durchschnitte 3.0",
    IFTA Journal 2012): NMA = (1+a)*MA1 - a*MA2, MA1 = MA(src, n1),
    MA2 = MA(MA1, n2), a = lam*(n1-1)/(n1-lam), lam = n1/n2.

    ``length2=0`` gives Duerschner's NWMA with the Nyquist lam = 2:
    MA2 length floor(n1/2) (CryptoStatistical's ``f_nwma``; for odd n1 Pine
    computes ``n/(n/2)`` = 2 in floats and truncates the WMA length). With
    ``length2`` set, lam = length/length2 (the OBV MACD ``nma()`` uses EMA and
    length2 = 26). ``ma_type`` is any ``tv_indicators`` MA name; Duerschner
    recommends WMA.
    """
    n = int(length)
    if int(length2) <= 0:
        return _nma(close, n, n // 2, 2.0, ma_type)
    return _nma(close, n, int(length2), n / int(length2), ma_type)


_OBV_TYPES = ("TDEMA", "TTEMA", "TEMA", "DEMA", "EMA", "AVG", "THMA", "ZLEMA", "ZLDEMA",
              "ZLTEMA", "DZLEMA", "TZLEMA", "LLEMA", "NMA")


def _dema(x, n):
    e = k.ema_nb(x, n)
    return 2 * e - k.ema_nb(e, n)


def _tema(x, n):
    e1 = k.ema_nb(x, n)
    e2 = k.ema_nb(e1, n)
    return 3 * (e1 - e2) + k.ema_nb(e2, n)


def _triple(f, x, n):
    m1 = f(x, n)
    m2 = f(m1, n)
    return 3 * (m1 - m2) + f(m2, n)


def _zl_src(x, n):
    return x + (x - shift_2d(x, _pround((n - 1) / 2)))


def _zlema(x, n):
    return k.ema_nb(_zl_src(x, n), n)


@indicator("OBV_MACD_MA", ["close"], ["ma"])
def obv_macd_ma(close, length=9, ma_type="DEMA", nma_length2=26):
    """The ``myma()`` selector of OBV MACD [RafaelZioni] (also Smooth HA
    Candles): TDEMA, TTEMA, TEMA, DEMA, EMA, AVG (= avg(TTEMA, TDEMA)), THMA,
    ZLEMA, ZLDEMA, ZLTEMA, DZLEMA, TZLEMA, LLEMA, NMA.

    T* = 3*(m1 - m2) + m3 over three chained copies of the base average
    (so THMA here is the TEMA formula on HMAs, not InSilico's THMA);
    ZL* use lag = round((len-1)/2); DZLEMA = 2*z1 - z2; LLEMA is the EMA of
    0.25*x + 0.5*x[1] + 0.25*x[2]; NMA is ``nma_durschner`` on EMAs with
    length2 = ``nma_length2``.
    """
    n = int(length)
    t = str(ma_type).strip().upper()
    if t not in _OBV_TYPES:
        raise ValueError(f"unknown ma_type {ma_type!r}; use one of {_OBV_TYPES}")
    x = close
    if t == "EMA":
        return k.ema_nb(x, n)
    if t == "DEMA":
        return _dema(x, n)
    if t == "TEMA":
        return _tema(x, n)
    if t == "TDEMA":
        return _triple(_dema, x, n)
    if t == "TTEMA":
        return _triple(_tema, x, n)
    if t == "AVG":
        return (_triple(_tema, x, n) + _triple(_dema, x, n)) / 2
    if t == "THMA":
        return _triple(hma_2d, x, n)
    if t == "ZLEMA":
        return _zlema(x, n)
    if t == "ZLDEMA":
        return _dema(_zl_src(x, n), n)
    if t == "ZLTEMA":
        return _tema(_zl_src(x, n), n)
    if t == "DZLEMA":
        z1 = _zlema(x, n)
        return 2 * z1 - _zlema(z1, n)
    if t == "TZLEMA":
        return _triple(_zlema, x, n)
    if t == "LLEMA":
        return k.ema_nb(0.25 * x + 0.5 * shift_2d(x, 1) + 0.25 * shift_2d(x, 2), n)
    n2 = int(nma_length2)
    return _nma(x, n, n2, n / n2, "ema")


@indicator("TILLSON_GD", ["close"], ["gd"])
def tillson_gd(close, length=5, vfactor=0.7):
    """Tillson's Generalized DEMA, the T3 building block:
    ema*(1+v) - ema(ema)*v (v = 1 is DEMA)."""
    n = int(length)
    e = k.ema_nb(close, n)
    return e * (1 + vfactor) - k.ema_nb(e, n) * vfactor


# ---------------------------------------------------------------------------
# Step / deadband lines
# ---------------------------------------------------------------------------

@njit(cache=True)
def _step_nb(src, band):
    out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        b = NAN
        for i in range(src.shape[0]):
            s = src[i, c]
            base = s if np.isnan(b) else b
            a = band[i, c]
            if s > base + a:
                b = s
            elif s < base - a:
                b = s
            else:
                b = base
            out[i, c] = b
    return out


@indicator("STEP_LINE", ["close", "band"], ["step"])
def step_line(close, band):
    """Deadband step line: follows the source only when it moves more than
    ``band`` away from the line, else holds (``b := src > nz(b[1],src) + a ?
    src : src < nz(b[1],src) - a ? src : nz(b[1],src)``). ``band`` is a series
    (``na`` holds the line). Used with various bands by T-Step LSMA,
    T-Channels, OBV MACD and the "Multi-indicator Combination" strategy."""
    return _step_nb(close, band)


@njit(cache=True)
def _tchannels_nb(src, mult):
    shape = src.shape
    line = np.full(shape, NAN)
    dev_o = np.full(shape, NAN)
    oc_o = np.full(shape, NAN)
    for c in range(shape[1]):
        b = NAN
        cum = 0.0
        seen = False
        dev = NAN
        oc = NAN
        for i in range(shape[0]):
            s = src[i, c]
            base = s if np.isnan(b) else b
            e = abs(s - base)
            if not np.isnan(e):
                cum += e
                seen = True
            a = cum / i * mult if (i > 0 and seen) else NAN
            bp = b
            if s > base + a:
                b = s
            elif s < base - a:
                b = s
            else:
                b = base
            ch = b - bp
            if not np.isnan(ch) and ch != 0:
                dev = a
            elif np.isnan(dev):
                dev = a
            if ch > 0:
                oc = 1.0
            elif ch < 0:
                oc = -1.0
            elif np.isnan(oc):
                oc = 0.0
            line[i, c] = b
            dev_o[i, c] = dev
            oc_o[i, c] = oc
    return line, dev_o, oc_o


@indicator("T_CHANNELS", ["close"], ["line", "band", "trend"])
def tchannels(close, mult=1.0):
    """T-Channels [alexgrover] step line, as reused in OBV MACD
    [RafaelZioni]: band a = cum(|src - b[1]|)/bar_index * mult, the step line
    b follows src only beyond +/- a; ``band`` is the a of the last step and
    ``trend`` +1/-1 by the direction of the last step (0 before any)."""
    return _tchannels_nb(close, float(mult))


@njit(cache=True)
def _tstep_nb(close, length, sc):
    shape = close.shape
    rows = shape[0]
    ls_o = np.full(shape, NAN)
    b_o = np.full(shape, NAN)
    osc_o = np.full(shape, NAN)
    n = length
    for c in range(shape[1]):
        src = np.full(rows, NAN)
        bb = np.full(rows, NAN)
        ls_prev = NAN
        alpha_f = NAN
        cum = 0.0
        osc = NAN
        b = NAN
        for i in range(rows):
            cl = close[i, c]
            s = sc * cl + (1 - sc) * (cl if np.isnan(ls_prev) else ls_prev)
            src[i] = s
            er = NAN
            if i >= n:
                den = 0.0
                for j in range(n):
                    den += abs(src[i - j] - src[i - j - 1])
                er = 1 - abs(s - src[i - n]) / den if den != 0 else NAN
            base = s if np.isnan(b) else b
            if not np.isnan(s):
                cum += abs(s - base)
            a = cum / i * (1 + er) if i > 0 else NAN
            bp = b
            if s > base + a:
                b = s
            elif s < base - a:
                b = s
            else:
                b = base
            bb[i] = b
            if b > bp:
                osc = 1.0
            elif b < bp:
                osc = 0.0
            ls = NAN
            if i >= n - 1:
                mx = 0.0
                my = 0.0
                for j in range(n):
                    mx += src[i - j]
                    my += bb[i - j]
                mx /= n
                my /= n
                sxy = 0.0
                sxx = 0.0
                syy = 0.0
                for j in range(n):
                    dx = src[i - j] - mx
                    dy = bb[i - j] - my
                    # Pine's stdev zeroes deviations within 1e-10, so a flat
                    # step line has stdev 0 and the fit is na (not noise)
                    if abs(dx) <= 1e-10:
                        dx = 0.0
                    if abs(dy) <= 1e-10:
                        dy = 0.0
                    sxy += dx * dy
                    sxx += dx * dx
                    syy += dy * dy
                if sxx > 0 and syy > 0:
                    alpha_f = sxy / math.sqrt(sxx * syy) * (math.sqrt(sxx / n) / math.sqrt(syy / n))
                ls = alpha_f * b + (mx - alpha_f * my)
            ls_prev = ls
            ls_o[i, c] = ls
            b_o[i, c] = b
            osc_o[i, c] = osc
    return ls_o, b_o, osc_o


@indicator("T_STEP_LSMA", ["close"], ["tstep", "step", "trend"])
def tstep_lsma(close, length=100, sc=0.5):
    """T-Step LSMA [alexgrover]: a step line b on a recursively smoothed
    source (src = sc*close + (1-sc)*ls[1]) with band
    cum(|src - b[1]|)/bar_index * (1 + er), then the least-squares fit of src
    on b over ``length`` bars: ls = alpha*b + beta with
    alpha = fixnan(correlation*stdev(src)/stdev(b)).

    As in Pine's ``ta.stdev``, deviations within 1e-10 count as 0, so while
    the step line is flat the fit is ``na`` and fixnan keeps the last alpha.
    ``tstep`` is the plotted ``ls`` (``na`` until the first fit; the script
    plots ``fixnan(ls)``), ``step`` is b, ``trend`` is 1 after an up step and
    0 after a down step.
    """
    return _tstep_nb(close, int(length), float(sc))


@njit(cache=True)
def _deadband_dsma_nb(src, dsrc, n, gamma):
    shape = src.shape
    rows = shape[0]
    out = np.full(shape, NAN)
    for c in range(shape[1]):
        xs = np.full(rows, NAN)
        inner = np.full(rows, NAN)
        mad = NAN
        cum = 0.0
        seen = False
        for i in range(rows):
            s = src[i, c]
            base = s if np.isnan(mad) else mad
            e = abs(dsrc[i - n, c] - base) if i >= n else NAN
            if not np.isnan(e):
                cum += e
                seen = True
            d = cum / i * gamma if (i > 0 and seen) else NAN
            if s > base + d:
                x = s + d
            elif s < base - d:
                x = s - d
            else:
                x = base
            xs[i] = x
            if i >= n - 1:
                t = 0.0
                for j in range(n):
                    t += xs[i - j]
                inner[i] = t / n
            mad = NAN
            if i >= 2 * n - 2:
                t = 0.0
                for j in range(n):
                    t += inner[i - j]
                mad = t / n
            out[i, c] = mad
    return out


@indicator("DEADBAND_DSMA", ["close", "deviation_source"], ["mad"])
def deadband_double_sma(close, deviation_source, length=15, gamma=4.0, zero_lag=False):
    """Double-SMA deadband average of the "Goblin Town" strategy
    (strategy-specific ``mad`` / ``mad4h``).

    d = cum(|dev_src[length] - mad[1]|)/bar_index * gamma; the source is
    clamped to mad[1] +/- d (moved by d when it breaks out) and smoothed by
    ``sma(sma(.., length), length)``. The script passes ``open`` (its input
    ``src``) as the deviation source but ``close`` as the price; pass
    ``close`` twice for the consistent version. ``zero_lag`` uses
    close + change(close, length/2). For ``mad4h`` pass the daily
    ``close[1]`` series (``request.security(.., lookahead_on)``).
    """
    n = int(length)
    src = close
    if zero_lag:
        src = close + (close - shift_2d(close, int(n / 2)))
    return _deadband_dsma_nb(src, deviation_source, n, float(gamma))


@njit(cache=True)
def _lazy_nb(x, lzf):
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        lz = NAN
        for i in range(x.shape[0]):
            v = x[i, c]
            vp = x[i - 1, c] if i > 0 else NAN
            sg = NAN if np.isnan(v) else (1.0 if v > 0 else (-1.0 if v < 0 else 0.0))
            up = lz + lzf * lz * sg
            dn = lz - lzf * lz * sg
            if v == (v if np.isnan(vp) else vp):
                lz = v
            elif v > (v if np.isnan(up) else up):
                lz = v
            elif v < (v if np.isnan(dn) else dn):
                lz = v
            out[i, c] = lz
    return out


@indicator("LAZY_LINE", ["close"], ["lazy"])
def hysteresis_filter(close, laziness=0.04):
    """"Lazy" hysteresis line (``lz()`` of the "Adaptive Grid" strategy,
    strategy-specific): holds its value until the source moves more than
    ``laziness`` (a fraction, 0.04 = 4%) away from it; it also follows
    the source whenever the source is unchanged from the previous bar."""
    return _lazy_nb(close, float(laziness))


@njit(cache=True)
def _rochla_nb(open_, close, hh, ll, recursive):
    out = np.full(close.shape, NAN)
    for c in range(close.shape[1]):
        d = NAN
        for i in range(close.shape[0]):
            a = (open_[i, c] if np.isnan(d) else d) if recursive else open_[i, c]
            rng = hh[i, c] - ll[i, c]
            b = abs(close[i, c] - a) / rng if rng != 0 else NAN
            cc = 1.0 if b > 1 else b
            d = cc * close[i, c] + (1 - cc) * (close[i, c] if np.isnan(d) else d)
            out[i, c] = d
    return out


@indicator("ROCHLA", ["open", "close", "range_high", "range_low"], ["rochla"])
def ratio_ochl_averager(open, close, range_high, range_low, recursive=False):
    """Ratio OCHL Averager [alexgrover]: an EMA whose alpha is the candle body
    relative to a reference range, c = min(|close - open|/(H - L), 1);
    d = c*close + (1-c)*d[1]. ``recursive=True`` measures the body from d[1].

    The strategy uses H/L = the previous higher-timeframe bar's high/low
    (``security(.., high[1], lookahead_on)``), which is not future data; build
    them with ``fmz_catalog.extra_tv.htf`` and pass them in.
    """
    return _rochla_nb(open, close, range_high, range_low, bool(recursive))


# ---------------------------------------------------------------------------
# Other recursive averages
# ---------------------------------------------------------------------------

@njit(cache=True)
def _rema_nb(src, a, lam, seed_price):
    out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        r1 = NAN
        r2 = NAN
        for i in range(src.shape[0]):
            x = src[i, c]
            if seed_price:
                p1 = x if np.isnan(r1) else r1
                p2 = p1 if np.isnan(r2) else r2
            else:
                p1 = 0.0 if np.isnan(r1) else r1
                p2 = 0.0 if np.isnan(r2) else r2
            v = (p1 + a * (x - p1) + lam * (2 * p1 - p2)) / (lam + 1)
            out[i, c] = v
            r2 = r1
            r1 = v
    return out


@indicator("REMA", ["close"], ["rema"])
def rema(close, length=10, lam=0.5, seed="zero"):
    """Regularized EMA (Chris Satchwell, TASC 2003):
    rema = (rema[1]*(1+2*lam) + alpha*(src - rema[1]) - lam*rema[2])/(1+lam),
    alpha = 2/(length+1). ``seed="zero"`` is the published nz(0) start (the
    strategy copy is exact); ``seed="price"`` starts at the first price."""
    return _rema_nb(close, 2.0 / (length + 1), float(lam), str(seed).lower() == "price")


@njit(cache=True)
def _ahrens_nb(src, n, seed_price):
    rows = src.shape[0]
    out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        for i in range(rows):
            x = src[i, c]
            p1 = out[i - 1, c] if i >= 1 else NAN
            pn = out[i - n, c] if i >= n else NAN
            if seed_price:
                p1 = x if np.isnan(p1) else p1
                pn = p1 if np.isnan(pn) else pn
            else:
                p1 = 0.0 if np.isnan(p1) else p1
                pn = 0.0 if np.isnan(pn) else pn
            out[i, c] = p1 + (x - (p1 + pn) / 2) / n
    return out


@indicator("AHRENS_MA", ["close"], ["ahma"])
def ahrens_ma(close, length=9, seed="zero"):
    """Ahrens Moving Average (Richard D. Ahrens, TASC Oct 2013):
    ahma = ahma[1] + (src - (ahma[1] + ahma[length])/2)/length.

    ``seed="zero"`` reproduces the scripts' ``nz()`` (exact copies);
    ``seed="price"`` starts at the first price and converges faster.
    """
    return _ahrens_nb(close, int(length), str(seed).lower() == "price")


@njit(cache=True)
def _smma2_nb(x, sma, n):
    """The ESSMA script's ``smma``: seeded by ``sma`` while smma[2] is na,
    then (smma[2]*(n-1) + x)/n (two interleaved recursions)."""
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for i in range(x.shape[0]):
            p2 = out[i - 2, c] if i >= 2 else NAN
            out[i, c] = sma[i, c] if np.isnan(p2) else (p2 * (n - 1) + x[i, c]) / n
    return out


@indicator("ESSMA", ["source", "open", "close"], ["essma"])
def essma(source, open, close, length=50, w1=2.0, w2=2.0, w3=2.0, w4=2.0, w5=2.0):
    """ESSMA [bhavishya] (strategy-specific):
    (smma + ema + sma - wma - rma + open + close)/3 of ``source``.

    Ported as published. Two quirks of the original: each MA is computed on
    src*w and divided by w again, so the weights cancel (they only change
    rounding); and its ``smma`` recurses on smma[2] instead of smma[1].
    """
    n = int(length)
    x4 = source * w4
    sm = _smma2_nb(x4, k.sma_nb(x4, n), float(n))
    return (sm / w4 + k.ema_nb(source * w2, n) / w2 + k.sma_nb(source * w1, n) / w1
            - k.wma_nb(source * w3, n) / w3 - k.rma_nb(source * w5, n) / w5 + open + close) / 3


@njit(cache=True)
def _cond_ema_nb(x, cond, n):
    out = np.full(x.shape, NAN)
    a = 2.0 / (n + 1)
    for c in range(x.shape[1]):
        e = NAN
        for i in range(x.shape[0]):
            if cond[i, c]:
                v = x[i, c]
                if np.isnan(e):
                    e = v
                e = (v - e) * a + e
            out[i, c] = e
    return out


@indicator("COND_EMA", ["close", "condition"], ["ema"])
def conditional_ema(close, condition, length=20):
    """Conditional-sampling EMA (``Cond_EMA`` of DonovanWall's Range Filter
    family): updates only on bars where ``condition`` is true, seeded with
    the first sampled value, otherwise holds."""
    cond = (np.nan_to_num(condition) != 0)
    return _cond_ema_nb(close, cond, float(length))


@njit(cache=True)
def _knn_nb(value, target, kn, window):
    out = np.full(value.shape, NAN)
    for c in range(value.shape[1]):
        dist = np.empty(kn)
        vals = np.empty(kn)
        for i in range(value.shape[0]):
            t = target[i, c]
            for j in range(kn):
                dist[j] = 1e10
                vals[j] = 0.0
            for lag in range(1, window + 1):
                if i - lag < 0:
                    break
                v = value[i - lag, c]
                dd = abs(t - v)
                mi = 0
                mv = dist[0]
                for j in range(1, kn):
                    if dist[j] > mv:
                        mi = j
                        mv = dist[j]
                if dd < mv:
                    dist[mi] = dd
                    vals[mi] = v
            full = True
            s = 0.0
            for j in range(kn):
                s += vals[j]
                if dist[j] == 1e10:
                    full = False
            if full:
                out[i, c] = s / kn
    return out


@indicator("KNN_MEAN", ["value", "target"], ["knn"])
def knn_mean(value, target, k_neighbors=3, window=30):
    """Mean of the ``k_neighbors`` values among value[1..window] closest to
    ``target`` (``meanOfKClosest`` of Zeiierman's kNN strategy). Same
    replacement order as the script; bars where fewer than k past values
    are available (the script averages its 0.0 placeholders) are ``na``.
    The strategy uses window = max(k, 30)."""
    return _knn_nb(value, target, int(k_neighbors), int(window))


@njit(cache=True)
def _rsx_nb(src, length):
    out = np.full(src.shape, NAN)
    f18 = 3.0 / (length + 2.0)
    f20 = 1.0 - f18
    for c in range(src.shape[1]):
        f90p = NAN
        f88p = NAN
        f8p = NAN
        f28 = f30 = f38 = f40 = f48 = f50 = f58 = f60 = f68 = f70 = f78 = f80 = NAN
        for i in range(src.shape[0]):
            z90 = 0.0 if np.isnan(f90p) else f90p
            z88 = 0.0 if np.isnan(f88p) else f88p
            if z90 == 0.0:
                f90_ = 1.0
            elif z88 <= z90:
                f90_ = z88 + 1
            else:
                f90_ = z90 + 1
            f88 = length - 1.0 if (z90 == 0.0 and length - 1 >= 5) else 5.0
            f8 = 100.0 * src[i, c]
            f10 = 0.0 if np.isnan(f8p) else f8p
            v8 = f8 - f10
            f28 = f20 * (0.0 if np.isnan(f28) else f28) + f18 * v8
            f30 = f18 * f28 + f20 * (0.0 if np.isnan(f30) else f30)
            vc = f28 * 1.5 - f30 * 0.5
            f38 = f20 * (0.0 if np.isnan(f38) else f38) + f18 * vc
            f40 = f18 * f38 + f20 * (0.0 if np.isnan(f40) else f40)
            v10 = f38 * 1.5 - f40 * 0.5
            f48 = f20 * (0.0 if np.isnan(f48) else f48) + f18 * v10
            f50 = f18 * f48 + f20 * (0.0 if np.isnan(f50) else f50)
            v14 = f48 * 1.5 - f50 * 0.5
            f58 = f20 * (0.0 if np.isnan(f58) else f58) + f18 * abs(v8)
            f60 = f18 * f58 + f20 * (0.0 if np.isnan(f60) else f60)
            v18 = f58 * 1.5 - f60 * 0.5
            f68 = f20 * (0.0 if np.isnan(f68) else f68) + f18 * v18
            f70 = f18 * f68 + f20 * (0.0 if np.isnan(f70) else f70)
            v1c = f68 * 1.5 - f70 * 0.5
            f78 = f20 * (0.0 if np.isnan(f78) else f78) + f18 * v1c
            f80 = f18 * f78 + f20 * (0.0 if np.isnan(f80) else f80)
            v20 = f78 * 1.5 - f80 * 0.5
            f0 = 1.0 if (f88 >= f90_ and f8 != f10) else 0.0
            f90 = 0.0 if (f88 == f90_ and f0 == 0.0) else f90_
            v4 = (v14 / v20 + 1.0) * 50.0 if (f88 < f90 and v20 > 0.0000000001) else 50.0
            out[i, c] = 100.0 if v4 > 100.0 else (0.0 if v4 < 0.0 else v4)
            f90p = f90_
            f88p = f88
            f8p = f8
    return out


@indicator("RSX", ["close"], ["rsx"])
def jurik_rsx(close, length=14):
    """Jurik RSX, the public port of Jurik's noise-free RSI (everget's /
    the MQL "RSX" chain f8..f90), 0..100. The strategy copy subtracts 50
    (centred at 0). 50 for the first bars while the f88/f90 counter warms up.
    """
    return _rsx_nb(close, float(length))


# ---------------------------------------------------------------------------
# Fourier smoothing and MoonFlag
# ---------------------------------------------------------------------------

@indicator("FTSMA", ["close"], ["ftsma"])
def ftsma(close, harmonic=1, ma_length=20, lookback=64, ma_type="ema"):
    """FTSMA [03.freeman] on xyse's Low-Frequency Fourier Transform.

    The signal is close + the amplitude of harmonic k of the DFT of the last
    ``lookback`` bars, evaluated at the current bar: 2/N * sum src[i]*cos(2*pi*k*i/N)
    (1/N for k = 0 or N/2; the sine term vanishes at i = 0). It is then
    smoothed with ``ma_type`` (any ``tv_indicators`` MA name, "alma",
    "swma" or "none"). The script's FRAMA option is not included.
    """
    nn = int(lookback)
    kk = int(harmonic)
    w = np.array([math.cos(2 * math.pi * kk * i / nn) for i in range(nn)])
    re = _fir_nb(close, w, 1.0)
    amp = re / nn if kk == 0 or kk * 2 == nn else 2 * re / nn
    return _ma(close + amp, int(ma_length), ma_type)


@indicator("MOONFLAG_AVG", ["close"], ["mfa"])
def moonflag_average(close, gaps=12):
    """MoonFlagAverage [MoonFlag] (strategy-specific): d(d(d(x))) where
    d(x) = wma(wma(wma(x, round((g - round(g/3))/2)), round(g/3)),
    int((g - round(g/3))/2))."""
    g = float(gaps)
    r3 = _pround(g / 3)
    l1 = max(_pround((g - r3) / 2), 1)
    l2 = max(r3, 1)
    l3 = max(int((g - r3) / 2), 1)
    y = close
    for _ in range(3):
        y = k.wma_nb(k.wma_nb(k.wma_nb(y, l1), l2), l3)
    return y


@indicator("RWMA_RANGE", ["high", "low", "close"], ["rwma"])
def rwma_range(high, low, close, length=20):
    """Range-weighted MA of TZack88's RMI Trend Sniper (``calculateRwma``):
    weight = (high-low)/sum(high-low, n); sum(close*weight, n)/sum(weight, n).
    """
    n = int(length)
    rng = high - low
    w = safe_div(rng, k.sum_nb(rng, n))
    return safe_div(k.sum_nb(close * w, n), k.sum_nb(w, n))


# Keep these out of tv_indicators' registry so the main library is unchanged.
EXTRA_MA = {name: REGISTRY.pop(name) for name in list(REGISTRY) if name not in _BEFORE}

__all__ = sorted(fn.__name__ for fn in EXTRA_MA.values())
