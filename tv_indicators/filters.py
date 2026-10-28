"""More moving averages and smoothing filters (adaptive, zero-lag, Ehlers)."""

import math

import numpy as np
from numba import njit

from . import kernels as k
from ._core import indicator, shift_2d

NAN = np.nan


# ---------------------------------------------------------------------------
# Kernels
# ---------------------------------------------------------------------------

@njit(cache=True)
def _var_nb(src, n, cmo_n):
    """Kivanc Ozbilgic's VAR / VIDYA. Starts from 0, exactly like the script."""
    out = np.full(src.shape, NAN)
    alpha = 2.0 / (n + 1.0)
    for c in range(src.shape[1]):
        prev = 0.0
        for i in range(src.shape[0]):
            ud = 0.0
            dd = 0.0
            ok = i >= cmo_n - 1
            if ok:
                for j in range(cmo_n):
                    if i - j - 1 < 0:
                        continue  # src[1] is na on the first bar: both terms 0
                    a = src[i - j, c]
                    b = src[i - j - 1, c]
                    if a > b:
                        ud += a - b
                    elif a < b:
                        dd += b - a
            cmo = (ud - dd) / (ud + dd) if ok and (ud + dd) != 0 else 0.0
            k_ = alpha * abs(cmo)
            prev = k_ * src[i, c] + (1 - k_) * prev
            out[i, c] = prev
    return out


@njit(cache=True)
def _supersmoother_nb(src, n):
    a1 = np.exp(-1.414 * np.pi / n)
    c2 = 2 * a1 * np.cos(1.414 * np.pi / n)
    c3 = -a1 * a1
    c1 = 1 - c2 - c3
    out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        s1 = 0.0
        s2 = 0.0
        for i in range(src.shape[0]):
            p1 = src[i - 1, c] if i > 0 else 0.0
            v = c1 * (src[i, c] + p1) / 2 + c2 * s1 + c3 * s2
            out[i, c] = v
            s2 = s1
            s1 = v
    return out


@njit(cache=True)
def _ultimate_smoother_nb(src, n):
    a1 = np.exp(-1.414 * np.pi / n)
    c2 = 2 * a1 * np.cos(1.414 * np.pi / n)
    c3 = -a1 * a1
    c1 = (1 + c2 - c3) / 4
    out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        for i in range(src.shape[0]):
            if i < 3:
                out[i, c] = src[i, c]
            else:
                out[i, c] = ((1 - c1) * src[i, c] + (2 * c1 - c2) * src[i - 1, c]
                             - (c1 + c3) * src[i - 2, c] + c2 * out[i - 1, c] + c3 * out[i - 2, c])
    return out


@njit(cache=True)
def _coral_nb(src, sm, cd):
    di = (sm - 1.0) / 2.0 + 1.0
    c1 = 2 / (di + 1.0)
    c2 = 1 - c1
    c3 = 3.0 * (cd * cd + cd * cd * cd)
    c4 = -3.0 * (2.0 * cd * cd + cd + cd * cd * cd)
    c5 = 3.0 * cd + 1.0 + cd * cd * cd + 3.0 * cd * cd
    out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        i1 = i2 = i3 = i4 = i5 = i6 = 0.0
        for i in range(src.shape[0]):
            i1 = c1 * src[i, c] + c2 * i1
            i2 = c1 * i1 + c2 * i2
            i3 = c1 * i2 + c2 * i3
            i4 = c1 * i3 + c2 * i4
            i5 = c1 * i4 + c2 * i5
            i6 = c1 * i5 + c2 * i6
            out[i, c] = -cd * cd * cd * i6 + c3 * i5 + c4 * i4 + c5 * i3
    return out


@njit(cache=True)
def _itrend_nb(src, a):
    it = np.full(src.shape, NAN)
    lag = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        for i in range(2, src.shape[0]):
            s0, s1, s2 = src[i, c], src[i - 1, c], src[i - 2, c]
            fb = (s0 + 2 * s1 + s2) / 4.0
            p1 = it[i - 1, c] if not np.isnan(it[i - 1, c]) else fb
            p2 = it[i - 2, c] if not np.isnan(it[i - 2, c]) else fb
            v = ((a - a * a / 4.0) * s0 + 0.5 * a * a * s1 - (a - 0.75 * a * a) * s2
                 + 2 * (1 - a) * p1 - (1 - a) * (1 - a) * p2)
            it[i, c] = v
            lag[i, c] = 2.0 * v - (0.0 if np.isnan(it[i - 2, c]) else it[i - 2, c])
    return it, lag


@njit(cache=True)
def _laguerre_nb(src, g):
    shape = src.shape
    l0o = np.full(shape, NAN)
    l1o = np.full(shape, NAN)
    l2o = np.full(shape, NAN)
    l3o = np.full(shape, NAN)
    for c in range(shape[1]):
        l0 = l1 = l2 = l3 = 0.0
        for i in range(shape[0]):
            n0 = (1 - g) * src[i, c] + g * l0
            n1 = -g * n0 + l0 + g * l1
            n2 = -g * n1 + l1 + g * l2
            n3 = -g * n2 + l2 + g * l3
            l0, l1, l2, l3 = n0, n1, n2, n3
            l0o[i, c] = l0
            l1o[i, c] = l1
            l2o[i, c] = l2
            l3o[i, c] = l3
    return l0o, l1o, l2o, l3o


@njit(cache=True)
def _frama_nb(price, high, low, n):
    out = np.full(price.shape, NAN)
    h = n // 2
    for c in range(price.shape[1]):
        prev = NAN
        d = NAN
        for i in range(price.shape[0]):
            if i >= n - 1:
                hh1 = high[i, c]
                ll1 = low[i, c]
                for j in range(h):
                    hh1 = max(hh1, high[i - j, c])
                    ll1 = min(ll1, low[i - j, c])
                hh2 = high[i - h, c]
                ll2 = low[i - h, c]
                for j in range(h, n):
                    hh2 = max(hh2, high[i - j, c])
                    ll2 = min(ll2, low[i - j, c])
                n1 = (hh1 - ll1) / h
                n2 = (hh2 - ll2) / h
                n3 = (max(hh1, hh2) - min(ll1, ll2)) / n
                if n1 > 0 and n2 > 0 and n3 > 0:
                    d = (np.log(n1 + n2) - np.log(n3)) / np.log(2.0)
            if np.isnan(d):
                cur = price[i, c]
            else:
                alpha = np.exp(-4.6 * (d - 1))
                alpha = min(max(alpha, 0.01), 1.0)
                cur = alpha * price[i, c] + (1 - alpha) * (price[i, c] if np.isnan(prev) else prev)
            out[i, c] = cur
            prev = cur
    return out


@njit(cache=True)
def _nw_endpoint_nb(src, h, window):
    out = np.full(src.shape, NAN)
    w = np.empty(window)
    for j in range(window):
        w[j] = np.exp(-(j * j) / (h * h * 2))
    den = w.sum()
    for c in range(src.shape[1]):
        for i in range(window - 1, src.shape[0]):
            s = 0.0
            for j in range(window):
                s += src[i - j, c] * w[j]
            out[i, c] = s / den
    return out


@njit(cache=True)
def _cog_nb(src, n):
    out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        for i in range(n - 1, src.shape[0]):
            num = 0.0
            den = 0.0
            for j in range(n):
                num += (j + 1) * src[i - j, c]
                den += src[i - j, c]
            if den != 0:
                out[i, c] = -num / den + (n + 1) / 2.0
    return out


# ---------------------------------------------------------------------------
# Indicators
# ---------------------------------------------------------------------------

@indicator("ZLEMA", ["close"], ["zlema"])
def zlema(close, length=20):
    """Zero-Lag EMA: ema(close + (close - close[lag]), length), lag=(length-1)//2."""
    n = int(length)
    return k.ema_nb(2 * close - shift_2d(close, (n - 1) // 2), n)


@indicator("T3", ["close"], ["t3"])
def t3(close, length=5, vfactor=0.7):
    """Tillson T3 (six chained EMAs). Same formula as TA-Lib's T3."""
    n = int(length)
    b = vfactor
    e1 = k.ema_nb(close, n)
    e2 = k.ema_nb(e1, n)
    e3 = k.ema_nb(e2, n)
    e4 = k.ema_nb(e3, n)
    e5 = k.ema_nb(e4, n)
    e6 = k.ema_nb(e5, n)
    c1 = -b ** 3
    c2 = 3 * b ** 2 + 3 * b ** 3
    c3 = -6 * b ** 2 - 3 * b - 3 * b ** 3
    c4 = 1 + 3 * b + b ** 3 + 3 * b ** 2
    return c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3


@indicator("SWMA", ["close"], ["swma"])
def swma(close):
    """``ta.swma``: fixed 4-bar symmetric weights 1/6, 2/6, 2/6, 1/6."""
    return (close + 2 * shift_2d(close, 1) + 2 * shift_2d(close, 2) + shift_2d(close, 3)) / 6


@indicator("VIDYA", ["close"], ["vidya"])
def vidya(close, length=9, cmo_length=9):
    """VIDYA / "VAR" as coded by KivancOzbilgic (used inside OTT).

    alpha = 2/(length+1) * |CMO(cmo_length)|. Like the script it starts at 0,
    so give it a few hundred bars of history before using it.
    """
    return _var_nb(close, int(length), int(cmo_length))


@indicator("TRIMA", ["close"], ["trima"])
def trima(close, length=20):
    """Triangular MA: sma(sma(close, ceil(n/2)), floor(n/2)+1). Matches TA-Lib."""
    n = int(length)
    return k.sma_nb(k.sma_nb(close, (n + 1) // 2), n // 2 + 1)


@indicator("EHMA", ["close"], ["ehma"])
def ehma(close, length=55):
    """Exponential Hull MA (Hull Suite [InSilico])."""
    n = int(length)
    return k.ema_nb(2 * k.ema_nb(close, n // 2) - k.ema_nb(close, n), int(math.floor(math.sqrt(n) + 0.5)))


@indicator("THMA", ["close"], ["thma"])
def thma(close, length=55):
    """Triple Hull MA (Hull Suite [InSilico]): wma(3*wma(n/3) - wma(n/2) - wma(n), n)."""
    n = int(length)
    inner = 3 * k.wma_nb(close, max(n // 3, 1)) - k.wma_nb(close, max(n // 2, 1)) - k.wma_nb(close, n)
    return k.wma_nb(inner, n)


@indicator("SUPERSMOOTHER", ["close"], ["supersmoother"])
def supersmoother(close, length=10):
    """Ehlers 2-pole Super Smoother, coded the usual Pine way (``nz`` seeding)."""
    return _supersmoother_nb(close, float(length))


@indicator("ULTIMATE_SMOOTHER", ["close"], ["ultimate_smoother"])
def ultimate_smoother(close, length=20):
    """Ehlers Ultimate Smoother (TASC, April 2024); first 3 bars equal the price."""
    return _ultimate_smoother_nb(close, float(length))


@indicator("MEDIAN", ["close"], ["median"])
def median(close, length=3):
    """``ta.median``: rolling median."""
    return k.median_nb(close, int(length))


@indicator("MIDPOINT", ["close"], ["midpoint"])
def midpoint(close, length=14):
    """(highest(close) + lowest(close)) / 2. Matches TA-Lib MIDPOINT."""
    n = int(length)
    return (k.highest_nb(close, n) + k.lowest_nb(close, n)) / 2


@indicator("MIDPRICE", ["high", "low"], ["midprice"])
def midprice(high, low, length=14):
    """(highest(high) + lowest(low)) / 2. Matches TA-Lib MIDPRICE."""
    n = int(length)
    return (k.highest_nb(high, n) + k.lowest_nb(low, n)) / 2


_GMMA_FAST = (3, 5, 8, 10, 12, 15)
_GMMA_SLOW = (30, 35, 40, 45, 50, 60)


@indicator("GMMA", ["close"], [f"ema{n}" for n in _GMMA_FAST + _GMMA_SLOW])
def gmma(close):
    """Guppy Multiple Moving Average: EMAs 3-15 (traders) and 30-60 (investors)."""
    return tuple(k.ema_nb(close, n) for n in _GMMA_FAST + _GMMA_SLOW)


@indicator("ZLSMA", ["close"], ["zlsma"])
def zlsma(close, length=32, offset=0):
    """Zero-Lag LSMA [veryfid]: lsma + (lsma - linreg(lsma))."""
    n, o = int(length), int(offset)
    l1 = k.linreg_nb(close, n, o)
    l2 = k.linreg_nb(l1, n, o)
    return 2 * l1 - l2


@indicator("MAVILIMW", ["close"], ["mavilimw"])
def mavilimw(close, first_length=3, second_length=5):
    """MavilimW [KivancOzbilgic]: six chained WMAs on Fibonacci-style lengths."""
    f, s = int(first_length), int(second_length)
    t = f + s
    ff = s + t
    ft = t + ff
    sm = ff + ft
    m = close
    for n in (f, s, t, ff, ft, sm):
        m = k.wma_nb(m, n)
    return m


@indicator("CORAL", ["close"], ["coral"])
def coral(close, smoothing=21, constant_d=0.4):
    """Coral Trend Indicator [LazyBear]. Starts from 0 like the script."""
    return _coral_nb(close, float(smoothing), float(constant_d))


@indicator("ITREND", ["high", "low"], ["itrend", "trigger"])
def itrend(high, low, alpha=0.07):
    """Ehlers Instantaneous Trendline [LazyBear] on hl2."""
    return _itrend_nb((high + low) / 2, float(alpha))


@indicator("NADARAYA_WATSON", ["close"], ["estimate", "upper", "lower"])
def nadaraya_watson(close, bandwidth=8.0, mult=3.0, window=500):
    """Nadaraya-Watson Envelope [LuxAlgo], non-repainting (endpoint) mode.

    Gaussian-kernel weighted average of the last ``window`` closes; the
    envelope is estimate +/- mult * sma(|close - estimate|, window - 1).
    The repainting mode redraws history and cannot be backtested honestly.
    """
    w = int(window)
    est = _nw_endpoint_nb(close, float(bandwidth), w)
    mae = k.sma_nb(np.abs(close - est), w - 1) * mult
    return est, est + mae, est - mae


@indicator("LAGUERRE", ["close"], ["laguerre"])
def laguerre(close, gamma=0.8):
    """Ehlers Laguerre filter: (L0 + 2*L1 + 2*L2 + L3) / 6."""
    l0, l1, l2, l3 = _laguerre_nb(close, float(gamma))
    return (l0 + 2 * l1 + 2 * l2 + l3) / 6


@indicator("LAGUERRE_RSI", ["close"], ["lrsi"])
def laguerre_rsi(close, gamma=0.5):
    """Laguerre RSI (Ehlers), 0..1 scale.

    Same formula as KivancOzbilgic's "Laguerre RSI" with gamma = 1 - alpha
    (his default alpha 0.2 is gamma 0.8; he plots x100).
    """
    l0, l1, l2, l3 = _laguerre_nb(close, float(gamma))
    cu = np.zeros(close.shape)
    cd = np.zeros(close.shape)
    for a, b in ((l0, l1), (l1, l2), (l2, l3)):
        cu += np.where(a >= b, a - b, 0.0)
        cd += np.where(a >= b, 0.0, b - a)
    tot = cu + cd
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(tot != 0, cu / tot, 0.0)


@indicator("FRAMA", ["high", "low"], ["frama"])
def frama(high, low, length=16):
    """Ehlers Fractal Adaptive MA on hl2 (``length`` is made even)."""
    n = int(length)
    n += n % 2
    return _frama_nb((high + low) / 2, high, low, n)


@indicator("CG", ["high", "low"], ["cg", "trigger"])
def center_of_gravity(high, low, length=10):
    """Ehlers Center of Gravity oscillator on hl2; ``trigger`` = cg[1]."""
    cg = _cog_nb((high + low) / 2, int(length))
    return cg, shift_2d(cg, 1)
