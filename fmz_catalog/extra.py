"""Staging area: best-version code for indicators that FMZ strategies use and
``tv_indicators`` does not have yet.

Nothing here is wired into ``tv_indicators``: importing this module moves its
indicators into ``EXTRA`` instead of the main registry, so the library and
its vectorbt classes are unchanged. Every function follows the same
conventions as ``tv_indicators`` (pandas/numpy in, same type out, a
namedtuple for several outputs) and documents its source.

    import fmz_catalog.extra as fx
    k, d, j = fx.kdj(df.high, df.low, df.close)
"""

import math

import numpy as np
from numba import njit

from tv_indicators import kernels as k
from tv_indicators._core import REGISTRY, indicator, safe_div, shift_2d

NAN = np.nan
_BEFORE = set(REGISTRY)


# ---------------------------------------------------------------------------
# Chinese-style smoothing (FMZ TA.KDJ, MyLanguage SMA/DMA, Tongdaxin/Wenhua)
# ---------------------------------------------------------------------------

@njit(cache=True)
def _sma_cn_nb(x, n, m, seed):
    """Y = (M*X + (N-M)*Y') / N, seeded with ``seed`` (NaN = first valid X)."""
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        y = seed
        for i in range(x.shape[0]):
            v = x[i, c]
            if np.isnan(v):
                out[i, c] = y
                continue
            y = v if np.isnan(y) else (m * v + (n - m) * y) / n
            out[i, c] = y
    return out


@indicator("SMA_CN", ["close"], ["sma_cn"])
def sma_cn(close, length=3, weight=1):
    """Chinese SMA(X,N,M) (MyLanguage/Tongdaxin): Y = (M*X + (N-M)*Y')/N.

    Not the same thing as TradingView's ``ta.sma``. SMA(X,N,1) is Wilder's
    smoothing (``ta.rma``) seeded with the first value instead of an SMA.
    """
    return _sma_cn_nb(close, float(length), float(weight), NAN)


@njit(cache=True)
def _dma_nb(x, a):
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        y = NAN
        for i in range(x.shape[0]):
            al = a[i, c]
            if np.isnan(x[i, c]) or np.isnan(al) or al <= 0 or al >= 1:
                out[i, c] = NAN if np.isnan(y) else y
                continue
            y = x[i, c] if np.isnan(y) else al * x[i, c] + (1 - al) * y
            out[i, c] = y
    return out


@indicator("DMA_CN", ["close", "alpha"], ["dma"])
def dma_cn(close, alpha):
    """MyLanguage DMA(X, A): exponential smoothing with a per-bar alpha series.

    Y = A*X + (1-A)*Y'; bars with A <= 0 or A >= 1 give no update (FMZ returns
    null there). Not the Chinese "DMA" indicator (MA10 - MA50).
    """
    return _dma_nb(close, alpha)


@njit(cache=True)
def _kdj_fmz_nb(rsv, n, kk, dd):
    shape = rsv.shape
    ko = np.full(shape, NAN)
    do = np.full(shape, NAN)
    for c in range(shape[1]):
        kp = 50.0
        dp = 50.0
        for i in range(shape[0]):
            if i >= n - 1:
                kp = (rsv[i, c] + (kk - 1) * kp) / kk
                dp = (kp + (dd - 1) * dp) / dd
                ko[i, c] = kp
                do[i, c] = dp
    return ko, do


@indicator("KDJ", ["high", "low", "close"], ["k", "d", "j"])
def kdj(high, low, close, length=9, k_smoothing=3, d_smoothing=3):
    """KDJ, the Chinese stochastic (FMZ ``TA.KDJ``, Tongdaxin, Wenhua).

    RSV = 100*(C - LLV(L,n)) / (HHV(H,n) - LLV(L,n));
    K = SMA(RSV, 3, 1), D = SMA(K, 3, 1) seeded at 50; J = 3K - 2D.
    Matches FMZ's open-source TA.KDJ bar for bar, except that a zero range
    keeps the previous K instead of turning every later value into NaN.
    """
    n = int(length)
    ll = k.lowest_nb(low, n)
    rng = k.highest_nb(high, n) - ll
    rsv = safe_div(close - ll, rng) * 100
    rsv = np.where(np.isnan(rsv) & ~np.isnan(rng), 50.0, rsv)  # flat window
    kk, dd = _kdj_fmz_nb(rsv, n, float(k_smoothing), float(d_smoothing))
    return kk, dd, 3 * kk - 2 * dd


@indicator("HV_LV", ["high", "low"], ["hv", "lv"])
def hv_lv(high, low, length=20):
    """Highest high / lowest low of the previous ``length`` bars, excluding the
    current bar: MyLanguage HV/LV and FMZ ``TA.Highest``/``TA.Lowest``.

    Equal to ``ta.highest(high, n)[1]``. The usual breakout channel.
    """
    n = int(length)
    return shift_2d(k.highest_nb(high, n), 1), shift_2d(k.lowest_nb(low, n), 1)


@indicator("STDEV_SAMPLE", ["close"], ["stdev"])
def stdev_sample(close, length=20):
    """Sample standard deviation (divide by n-1): MyLanguage ``STD``,
    ``ta.stdev(x, n, biased=false)``, pandas ``.std()``."""
    n = int(length)
    return k.stdev_nb(close, n) * math.sqrt(n / (n - 1))


# ---------------------------------------------------------------------------
# Moving averages and filters used by FMZ scripts
# ---------------------------------------------------------------------------

@indicator("TSF", ["close"], ["tsf"])
def tsf(close, length=14):
    """Time Series Forecast: the regression line projected one bar ahead.

    linreg(close, n, 0) + slope, which equals TA-Lib TSF and the
    ``Tsf_Func`` used in Kivanc's OTT-family scripts.
    """
    n = int(length)
    return k.linreg_nb(close, n, -1)


@njit(cache=True)
def _wwma_nb(x, n):
    out = np.full(x.shape, NAN)
    a = 1.0 / n
    for c in range(x.shape[1]):
        y = 0.0
        for i in range(x.shape[0]):
            v = x[i, c]
            y = a * v + (1 - a) * y if not np.isnan(v) else y
            out[i, c] = y
    return out


@indicator("WWMA", ["close"], ["wwma"])
def wwma(close, length=14):
    """Welles Wilder MA as coded in Kivanc's scripts (``Wwma_Func``).

    Same recursion as ``ta.rma`` but seeded at 0 (``nz(WWMA[1])``), so it
    needs several times ``length`` bars to converge. Use ``tv.rma`` unless you
    need to reproduce those scripts exactly.
    """
    return _wwma_nb(close, float(length))


@indicator("ZLEMA_HALF_LAG", ["close"], ["zlema"])
def zlema_half_lag(close, length=20):
    """ZLEMA with lag = floor(length/2), as in Kivanc's ``Zlema_Func``.

    ``tv_indicators.zlema`` uses Ehlers' lag (length-1)/2; the two differ for
    even lengths.
    """
    n = int(length)
    return k.ema_nb(2 * close - shift_2d(close, n // 2), n)


@njit(cache=True)
def _iir_nb(x, b0, a):
    """y = b0*x + a[0]*y[1] + a[1]*y[2] + ...; history before bar 0 is 0 (nz)."""
    p = a.shape[0]
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        hist = np.zeros(p)
        for i in range(x.shape[0]):
            v = b0 * (0.0 if np.isnan(x[i, c]) else x[i, c])
            for j in range(p):
                v += a[j] * hist[j]
            for j in range(p - 1, 0, -1):
                hist[j] = hist[j - 1]
            hist[0] = v
            out[i, c] = v
    return out


@indicator("SSF2", ["close"], ["ssf"])
def ssf2(close, length=10):
    """Ehlers 2-pole Super Smoother, "Cycle Analytics" form (``get2PoleSSF``).

    ssf = c1*src + c2*ssf[1] + c3*ssf[2] with arg = sqrt(2)*pi/length. Unlike
    ``tv.supersmoother`` (Ehlers 2013) it does not average src and src[1].
    """
    arg = math.sqrt(2) * math.pi / length
    a1 = math.exp(-arg)
    c2 = 2 * a1 * math.cos(arg)
    c3 = -a1 * a1
    return _iir_nb(close, 1 - c2 - c3, np.array([c2, c3]))


@indicator("SSF3", ["close"], ["ssf"])
def ssf3(close, length=10):
    """Ehlers 3-pole Super Smoother (``get3PoleSSF``)."""
    arg = math.pi / length
    a1 = math.exp(-arg)
    b1 = 2 * a1 * math.cos(1.738 * arg)
    c1 = a1 * a1
    c2, c3, c4 = b1 + c1, -(c1 + b1 * c1), c1 * c1
    return _iir_nb(close, 1 - c2 - c3 - c4, np.array([c2, c3, c4]))


def _gauss_alpha(period, poles, root2=math.sqrt(2)):
    beta = (1 - math.cos(2 * math.pi / period)) / (math.pow(root2, 2.0 / poles) - 1)
    return -beta + math.sqrt(beta * beta + 2 * beta)


def _gauss_2d(x, period, poles, root2=math.sqrt(2)):
    al = _gauss_alpha(period, poles, root2)
    co = np.array([(-1) ** (j + 2) * math.comb(poles, j + 1) * (1 - al) ** (j + 1) for j in range(poles)])
    return _iir_nb(x, al ** poles, co)


@indicator("GAUSSIAN", ["close"], ["gaussian"])
def gaussian_filter(close, period=14, poles=4):
    """Ehlers Gaussian filter with 1-9 poles (zero-seeded, as the Pine ports)."""
    return _gauss_2d(close, float(period), int(poles))


@indicator("GAUSSIAN_CHANNEL", ["high", "low", "close"], ["filter", "upper", "lower"])
def gaussian_channel(high, low, close, period=144, poles=4, mult=1.414, reduced_lag=False, fast_response=False):
    """Gaussian Channel [DonovanWall]: Gaussian filter of hlc3, bands from the
    Gaussian-filtered true range x ``mult``. Uses the script's 1.414 for sqrt(2)."""
    src = (high + low + close) / 3
    tr = k.tr_nb(high, low, close, True)
    lag = int((period - 1) / (2 * poles))
    if reduced_lag:
        src = src + (src - shift_2d(src, lag))
        tr = tr + (tr - shift_2d(tr, lag))
    f = _gauss_2d(src, float(period), int(poles), 1.414)
    ft = _gauss_2d(tr, float(period), int(poles), 1.414)
    if fast_response:
        f = (f + _gauss_2d(src, float(period), 1, 1.414)) / 2
        ft = (ft + _gauss_2d(tr, float(period), 1, 1.414)) / 2
    return f, f + ft * mult, f - ft * mult


@njit(cache=True)
def _jma_nb(src, length, phase, power):
    out = np.full(src.shape, NAN)
    pr = 0.5 if phase < -100 else (2.5 if phase > 100 else phase / 100 + 1.5)
    beta = 0.45 * (length - 1) / (0.45 * (length - 1) + 2)
    alpha = beta ** power
    for c in range(src.shape[1]):
        e0 = e1 = e2 = j = 0.0
        for i in range(src.shape[0]):
            s = src[i, c]
            e0 = (1 - alpha) * s + alpha * e0
            e1 = (s - e0) * (1 - beta) + beta * e1
            e2 = (e0 + pr * e1 - j) * (1 - alpha) ** 2 + alpha ** 2 * e2
            j = e2 + j
            out[i, c] = j
    return out


@indicator("JMA", ["close"], ["jma"])
def jma(close, length=7, phase=50, power=2):
    """Jurik Moving Average, the open approximation in [everget]'s TV script
    (Jurik's real JMA is proprietary). Zero-seeded like the script."""
    return _jma_nb(close, float(length), float(phase), float(power))


@njit(cache=True)
def _mama_nb(price, fast, slow):
    n, m = price.shape
    mama = np.full(price.shape, NAN)
    fama = np.full(price.shape, NAN)
    for c in range(m):
        sm = np.zeros(n)
        de = np.zeros(n)
        q1 = np.zeros(n)
        i1 = np.zeros(n)
        i2 = np.zeros(n)
        q2 = np.zeros(n)
        re = np.zeros(n)
        im = np.zeros(n)
        per = np.zeros(n)
        sper = np.zeros(n)
        ph = np.zeros(n)
        ma = 0.0
        fa = 0.0
        for i in range(n):
            p = price[i, c]
            if i < 5:
                mama[i, c] = NAN
                ma = p
                fa = p
                continue
            sm[i] = (4 * p + 3 * price[i - 1, c] + 2 * price[i - 2, c] + price[i - 3, c]) / 10
            adj = 0.075 * per[i - 1] + 0.54
            de[i] = (0.0962 * sm[i] + 0.5769 * sm[i - 2] - 0.5769 * sm[i - 4] - 0.0962 * sm[i - 6]) * adj if i >= 6 else 0.0
            q1[i] = (0.0962 * de[i] + 0.5769 * de[i - 2] - 0.5769 * de[i - 4] - 0.0962 * de[i - 6]) * adj if i >= 6 else 0.0
            i1[i] = de[i - 3]
            ji = (0.0962 * i1[i] + 0.5769 * i1[i - 2] - 0.5769 * i1[i - 4] - 0.0962 * i1[i - 6]) * adj if i >= 6 else 0.0
            jq = (0.0962 * q1[i] + 0.5769 * q1[i - 2] - 0.5769 * q1[i - 4] - 0.0962 * q1[i - 6]) * adj if i >= 6 else 0.0
            i2[i] = 0.2 * (i1[i] - jq) + 0.8 * i2[i - 1]
            q2[i] = 0.2 * (q1[i] + ji) + 0.8 * q2[i - 1]
            re[i] = 0.2 * (i2[i] * i2[i - 1] + q2[i] * q2[i - 1]) + 0.8 * re[i - 1]
            im[i] = 0.2 * (i2[i] * q2[i - 1] - q2[i] * i2[i - 1]) + 0.8 * im[i - 1]
            pr = per[i - 1]
            if im[i] != 0 and re[i] != 0:
                pr = 360.0 / math.degrees(math.atan(im[i] / re[i]))
            if pr > 1.5 * per[i - 1]:
                pr = 1.5 * per[i - 1]
            if pr < 0.67 * per[i - 1]:
                pr = 0.67 * per[i - 1]
            pr = min(max(pr, 6.0), 50.0)
            per[i] = 0.2 * pr + 0.8 * per[i - 1]
            sper[i] = 0.33 * per[i] + 0.67 * sper[i - 1]
            ph[i] = math.degrees(math.atan(q1[i] / i1[i])) if i1[i] != 0 else ph[i - 1]
            dp = ph[i - 1] - ph[i]
            if dp < 1:
                dp = 1.0
            al = fast / dp
            if al < slow:
                al = slow
            ma = al * p + (1 - al) * ma
            fa = 0.5 * al * ma + (1 - 0.5 * al) * fa
            mama[i, c] = ma
            fama[i, c] = fa
    return mama, fama


@indicator("MAMA", ["close"], ["mama", "fama"])
def mama(close, fast_limit=0.5, slow_limit=0.05):
    """Ehlers MESA Adaptive Moving Average (MAMA/FAMA), from Ehlers'
    published EasyLanguage. Converges to TA-Lib's MAMA after its warm-up."""
    return _mama_nb(close, float(fast_limit), float(slow_limit))


# ---------------------------------------------------------------------------
# DMI variant and HPotter's 123 Reversal
# ---------------------------------------------------------------------------

@njit(cache=True)
def _adx_sma_nb(high, low, close, n):
    shape = close.shape
    dip = np.full(shape, NAN)
    dim = np.full(shape, NAN)
    dx = np.full(shape, NAN)
    for c in range(shape[1]):
        s_tr = 0.0
        s_p = 0.0
        s_m = 0.0
        for i in range(shape[0]):
            pc = close[i - 1, c] if i > 0 else 0.0
            ph = high[i - 1, c] if i > 0 else 0.0
            pl = low[i - 1, c] if i > 0 else 0.0
            tr = max(max(high[i, c] - low[i, c], abs(high[i, c] - pc)), abs(low[i, c] - pc))
            up = high[i, c] - ph
            dn = pl - low[i, c]
            dmp = max(up, 0.0) if up > dn else 0.0
            dmm = max(dn, 0.0) if dn > up else 0.0
            s_tr = s_tr - s_tr / n + tr
            s_p = s_p - s_p / n + dmp
            s_m = s_m - s_m / n + dmm
            p = s_p / s_tr * 100 if s_tr != 0 else NAN
            mm = s_m / s_tr * 100 if s_tr != 0 else NAN
            dip[i, c] = p
            dim[i, c] = mm
            dx[i, c] = abs(p - mm) / (p + mm) * 100 if (p + mm) != 0 else NAN
    return dip, dim, dx


@indicator("ADX_SMA", ["high", "low", "close"], ["plus_di", "minus_di", "adx"])
def adx_sma(high, low, close, length=14):
    """"ADX and DI" [BeikabuOyaji / MasaNakamura], used by ~40 FMZ strategies.

    Wilder running sums (S = S - S/n + x, seeded at 0, first-bar TR uses
    close[1] = 0) and **ADX = sma(DX, n)**. TradingView's DMI smooths DX with
    RMA instead, so the ADX line differs permanently; the DI lines converge.
    """
    n = int(length)
    p, m, dx = _adx_sma_nb(high, low, close, float(n))
    return p, m, k.sma_nb(dx, n)


@njit(cache=True)
def _rev123_nb(close, fast, slow, level):
    out = np.zeros(close.shape)
    for c in range(close.shape[1]):
        pos = 0.0
        for i in range(close.shape[0]):
            if i >= 2:
                c0, c1, c2 = close[i, c], close[i - 1, c], close[i - 2, c]
                f, s = fast[i, c], slow[i, c]
                if c2 < c1 and c0 > c1 and f < s and f > level:
                    pos = 1.0
                elif c2 > c1 and c0 < c1 and f > s and f < level:
                    pos = -1.0
            out[i, c] = pos
    return out


@indicator("REVERSAL123", ["high", "low", "close"], ["pos", "k", "d"])
def reversal_123(high, low, close, length=14, k_smoothing=1, d_length=3, level=50):
    """123 Reversal [HPotter] (Ulf Jensen, "Street Smarts"), used by 128 FMZ
    combo strategies. ``pos`` is 1 / -1 / previous (0 at the start)."""
    st = safe_div(close - k.lowest_nb(low, int(length)),
                  k.highest_nb(high, int(length)) - k.lowest_nb(low, int(length))) * 100
    fast = k.sma_nb(st, int(k_smoothing))
    slow = k.sma_nb(fast, int(d_length))
    return _rev123_nb(close, fast, slow, float(level)), fast, slow


# ---------------------------------------------------------------------------
# Price structure
# ---------------------------------------------------------------------------

@indicator("FVG", ["high", "low"], ["bull", "bear", "bull_top", "bull_bottom", "bear_top", "bear_bottom"])
def fair_value_gap(high, low):
    """Fair Value Gaps (ICT / SMC), known on the bar that completes them.

    Bullish gap when low > high[2] (zone high[2] .. low); bearish when
    high < low[2] (zone high .. low[2]). Zones are NaN on bars without a gap.
    """
    h2, l2 = shift_2d(high, 2), shift_2d(low, 2)
    with np.errstate(invalid="ignore"):
        bull = low > h2
        bear = high < l2
    return (bull, bear, np.where(bull, low, NAN), np.where(bull, h2, NAN),
            np.where(bear, l2, NAN), np.where(bear, high, NAN))


@indicator("FIB_LEVELS", ["high", "low"], ["l0", "l236", "l382", "l500", "l618", "l786", "l100"])
def fib_levels(high, low, length=100):
    """Fibonacci retracement levels of the rolling ``length``-bar range,
    measured down from the high (l0 = high, l100 = low)."""
    n = int(length)
    hh = k.highest_nb(high, n)
    ll = k.lowest_nb(low, n)
    r = hh - ll
    return tuple(hh - r * f for f in (0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0))


# ---------------------------------------------------------------------------
# Pine helpers that vectorbt does not have
# ---------------------------------------------------------------------------

@indicator("RISING_FALLING", ["close"], ["rising", "falling"])
def rising_falling(close, length=3):
    """``ta.rising`` / ``ta.falling``: strictly higher (lower) than each of
    the previous ``length`` values."""
    n = int(length)
    r = np.ones(close.shape, dtype=bool)
    f = np.ones(close.shape, dtype=bool)
    with np.errstate(invalid="ignore"):
        for j in range(1, n + 1):
            p = shift_2d(close, j)
            r &= close > p
            f &= close < p
    return r, f


@njit(cache=True)
def _valuewhen_nb(cond, src, occ):
    out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        hist = np.full(occ + 1, NAN)
        for i in range(src.shape[0]):
            if cond[i, c]:
                for j in range(occ, 0, -1):
                    hist[j] = hist[j - 1]
                hist[0] = src[i, c]
            out[i, c] = hist[occ]
    return out


@indicator("VALUEWHEN", ["condition", "close"], ["value"])
def valuewhen(condition, close, occurrence=0):
    """``ta.valuewhen(cond, src, occurrence)``."""
    return _valuewhen_nb(np.nan_to_num(condition) != 0, close, int(occurrence))


@indicator("BARSSINCE", ["condition"], ["bars"])
def barssince(condition):
    """``ta.barssince(cond)``; NaN before the first true bar."""
    return k.barssince_nb(np.nan_to_num(condition) != 0)


@njit(cache=True)
def _percentile_nb(x, n, pct, interp):
    out = np.full(x.shape, NAN)
    buf = np.empty(n)
    for c in range(x.shape[1]):
        for i in range(n - 1, x.shape[0]):
            ok = True
            for j in range(n):
                v = x[i - j, c]
                if np.isnan(v):
                    ok = False
                    break
                buf[j] = v
            if not ok:
                continue
            s = np.sort(buf)
            if interp:
                pos = pct / 100.0 * (n - 1)
                lo = int(math.floor(pos))
                hi = min(lo + 1, n - 1)
                out[i, c] = s[lo] + (s[hi] - s[lo]) * (pos - lo)
            else:
                rank = int(math.ceil(pct / 100.0 * n))
                out[i, c] = s[max(rank, 1) - 1]
    return out


@indicator("PERCENTILE", ["close"], ["percentile"])
def percentile(close, length=20, percentage=50.0, method="linear"):
    """``ta.percentile_linear_interpolation`` (method="linear") or
    ``ta.percentile_nearest_rank`` (method="nearest")."""
    return _percentile_nb(close, int(length), float(percentage), str(method).lower() == "linear")


# Keep these out of tv_indicators' registry so the main library is unchanged.
EXTRA = {name: REGISTRY.pop(name) for name in list(REGISTRY) if name not in _BEFORE}

__all__ = sorted(fn.__name__ for fn in EXTRA.values())
