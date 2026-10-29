"""Staging area: oscillators, volume and statistics indicators that FMZ
strategies use and ``tv_indicators`` does not have yet.

Same conventions as :mod:`fmz_catalog.extra`: every core takes 2D float
arrays, the ``@indicator`` wrapper gives pandas/numpy in and the same type
out (a namedtuple for several outputs), and importing this module moves its
indicators into ``EXTRA_MISC`` instead of the main registry, so
``tv_indicators`` and its vectorbt classes are unchanged.

Pine semantics are kept on purpose: comparisons with ``na`` are false,
``nz()`` seeds recursions with 0, ``x[n]`` is ``na`` before bar ``n`` and
``x / 0`` is ``na``. Nothing looks ahead: every value uses the current and
past bars only. Indicators that only exist in one strategy are marked
"strategy-specific" and are faithful ports of that strategy's code.

    import fmz_catalog.extra_misc as fm
    nw = fm.nadaraya_watson_rq(df.close)          # jdehorty, h=8, r=8, x_0=25
    vp = fm.volume_profile(df.high, df.low, df.volume, length=100)
"""

import math

import numpy as np
from numba import njit

from tv_indicators import kernels as k
from tv_indicators._core import REGISTRY, change_2d, indicator, ma_2d, safe_div, shift_2d
from tv_indicators.oscillators import rsi_2d, stoch_2d

NAN = np.nan
_BEFORE = set(REGISTRY)


def _gt(a, b):
    """Pine ``a > b``: false when either side is na."""
    with np.errstate(invalid="ignore"):
        return np.greater(a, b)


def _lt(a, b):
    with np.errstate(invalid="ignore"):
        return np.less(a, b)


def _pmax(a, b):
    """Pine ``math.max``: na when either argument is na."""
    out = np.maximum(a, b)  # np.maximum already propagates NaN
    return out


def _pmin(a, b):
    return np.minimum(a, b)


# ---------------------------------------------------------------------------
# Volume RSI (RSI_Volume with WiMA)
# ---------------------------------------------------------------------------

@njit(cache=True)
def _wima0_nb(x, n):
    """``MA := (src + nz(MA[1] * (n-1))) / n``: Wilder MA seeded at 0.

    An na input gives na, and the bar after it restarts from 0 (``nz``)."""
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        prev = NAN
        for i in range(x.shape[0]):
            p = 0.0 if np.isnan(prev) else prev * (n - 1)
            y = (x[i, c] + p) / n
            out[i, c] = y
            prev = y
    return out


@indicator("VOLUME_RSI", ["close", "volume"], ["rsi"])
def volume_rsi(close, volume, length=14):
    """Volume RSI (``RSI_Volume`` / ``calc_rsi_volume``): RSI of
    volume-weighted price changes.

    up = change > 0 ? |change| * volume : 0 (dn likewise), each smoothed with
    ``WiMA`` (Wilder's recursion seeded at 0, not SMA-seeded like ``ta.rma``),
    RSI = 100 * up / (up + dn). The function is shared verbatim by five FMZ
    strategies (Johny's BOT, Dual Laser, Quant Trend, Indicator Verification,
    exlux99's RSI Curve); its first publisher could not be traced.
    """
    n = float(length)
    ch = change_2d(close)
    mag = np.abs(ch) * volume
    up = np.where(_gt(ch, 0), mag, 0.0)
    dn = np.where(_lt(ch, 0), mag, 0.0)
    upt = _wima0_nb(up, n)
    dnt = _wima0_nb(dn, n)
    return 100 * safe_div(upt, upt + dnt)


# ---------------------------------------------------------------------------
# VuManChu Cipher B: RSI+MFI area
# ---------------------------------------------------------------------------

@indicator("CIPHER_B_RSIMFI", ["open", "high", "low", "close"], ["rsimfi"])
def cipher_b_rsimfi(open, high, low, close, period=60, multiplier=150.0, pos_y=2.5):
    """VuManChu Cipher B "RSI+MFI Area" (``f_rsimfi``):
    ``sma((close - open) / (high - low) * multiplier, period) - pos_y``.

    Despite its name it is neither RSI nor MFI. A flat bar (high == low)
    gives na, which keeps the SMA na for ``period`` bars, as in Pine. The
    script wraps it in ``request.security`` for other timeframes; this is
    the chart-timeframe value.
    """
    body = safe_div(close - open, high - low) * float(multiplier)
    return k.sma_nb(body, int(period)) - float(pos_y)


# ---------------------------------------------------------------------------
# RedK VADER (Volume-Accelerated Directional Energy Ratio)
# ---------------------------------------------------------------------------

_V_CALC = {"relative": 0, "full": 1, "none": 2}


@indicator("REDK_VADER", ["high", "low", "close", "volume"],
           ["demand", "supply", "vader", "signal", "sentiment"])
def redk_vader(high, low, close, volume, length=10, der_avg=5, ma_type="WMA", smooth=3,
               senti=20, v_calc="Relative", vlookbk=20):
    """RedK Dual VADER with Energy Bars (VADER v4.0, same core as v3.0) [RedKTrader].

    Defaults are v4.0's (v3.0 used length 9 and volume lookback 10).
    ``demand``/``supply`` are the Demand/Supply Energy lines (adp/asp),
    ``vader`` = adp - asp, ``signal`` = wma(vader, smooth) (the plotted line,
    crossing 0 is the signal) and ``sentiment`` the longer-length VADER.

    The "Relative" volume is ``ta.stoch(v, highest(v,n), lowest(v,n), n)/100``
    as published, so its effective window is 2n-1 bars.
    """
    n = int(length)
    mode = _V_CALC[str(v_calc).strip().lower()]
    if mode == 0:
        lb = int(vlookbk)
        vola = stoch_2d(volume, k.highest_nb(volume, lb), k.lowest_nb(volume, lb), lb) / 100
    elif mode == 1:
        vola = volume.copy()
    else:
        vola = np.ones(volume.shape)
    vola = np.where(np.isnan(volume), 1.0, vola)
    r = (k.highest_nb(high, 2) - k.lowest_nb(low, 2)) / 2
    sr = safe_div(change_2d(close), r)
    rsr = _pmax(_pmin(sr, 1.0), -1.0)
    cc = k.fixnan_nb(rsr * vola)
    c_plus = _pmax(cc, 0.0)
    c_minus = -_pmin(cc, 0.0)
    avg_vola = ma_2d(vola, n, ma_type)
    dem = safe_div(ma_2d(c_plus, n, ma_type), avg_vola)
    sup = safe_div(ma_2d(c_minus, n, ma_type), avg_vola)
    adp = 100 * k.wma_nb(dem, int(der_avg))
    asp = 100 * k.wma_nb(sup, int(der_avg))
    anp = adp - asp
    anp_s = k.wma_nb(anp, int(smooth))
    s_adp = 100 * k.wma_nb(dem, int(senti))
    s_asp = 100 * k.wma_nb(sup, int(senti))
    v_senti = k.wma_nb(s_adp - s_asp, int(smooth))
    return adp, asp, anp, anp_s, v_senti


# ---------------------------------------------------------------------------
# jdehorty: Nadaraya-Watson Rational Quadratic Kernel (Non-Repainting)
# ---------------------------------------------------------------------------

@njit(cache=True)
def _rq_kernel_nb(x, h, r, m):
    """sum_{i=0}^{m-1} x[i] w_i / sum w_i, w_i = (1 + i^2 / (2 r h^2))^-r."""
    w = np.empty(m)
    for i in range(m):
        w[i] = (1.0 + (i * i) / (h * h * 2.0 * r)) ** (-r)
    sw = w.sum()
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for t in range(m - 1, x.shape[0]):
            s = 0.0
            for i in range(m):
                s += x[t - i, c] * w[i]  # na anywhere -> na, as in the Pine loop
            out[t, c] = s / sw
    return out


@indicator("NADARAYA_WATSON_RQ", ["close"], ["yhat1", "yhat2"])
def nadaraya_watson_rq(close, h=8.0, r=8.0, x_0=25, lag=2, size=1):
    """Nadaraya-Watson: Rational Quadratic Kernel (Non-Repainting) [jdehorty].

    yhat = sum_{i=0}^{size+x_0} src[i] w_i / sum w_i with
    w_i = (1 + i^2 / (2 r h^2))^-r. ``size`` is
    ``array.size(array.from(src))`` = 1 in the script, so the default kernel
    spans x_0 + 2 = 27 bars and is na before that. ``yhat1`` uses bandwidth
    ``h``, ``yhat2`` uses ``h - lag`` (the script's crossover line). Same as
    ``rationalQuadratic`` in jdehorty's KernelFunctions library.
    """
    m = int(size) + int(x_0) + 1
    y1 = _rq_kernel_nb(close, float(h), float(r), m)
    y2 = _rq_kernel_nb(close, float(h) - float(lag), float(r), m)
    return y1, y2


# ---------------------------------------------------------------------------
# Kharevsky's P-Signal
# ---------------------------------------------------------------------------

def _erf_nr(x):
    """The script's ``fErf``: Numerical Recipes erfc (Chebyshev), |err| < 1.2e-7."""
    t = 1.0 / (1.0 + 0.5 * np.abs(x))
    ans = 1.0 - t * np.exp(-x * x - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (
        -0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))))
    with np.errstate(invalid="ignore"):
        return np.where(x >= 0, ans, -ans)


@indicator("P_SIGNAL", ["close"], ["psignal", "raw"])
def p_signal(close, points=9, version=4):
    """P-Signal [Kharevsky]: ``sma(fPSignal(change(src), n), n)``, n = points-1.

    fPSignal = erf(sma(x, n) / stdev(x, n) / sqrt 2), the probability-like
    sign of the mean change. Kharevsky passes ``ohlc4`` as ``src``.
    ``version=4`` (P-Signal Strategy, v4 script) evaluates erf(1) when the
    stdev is not > 0, so warm-up bars are 0.8427 rather than na;
    ``version=5`` (P-Signal Strategy RVS) uses sign(sma) instead and is na
    during the warm-up.
    """
    n = int(points) - 1
    x = change_2d(close)
    sd = k.stdev_nb(x, n)
    m = k.sma_nb(x, n)
    pos = _gt(sd, 0)
    z = safe_div(m, sd) / math.sqrt(2)
    if int(version) >= 5:
        raw = np.where(pos, _erf_nr(z), np.sign(m))
    else:
        raw = _erf_nr(np.where(pos, z, 1.0))
    return k.sma_nb(raw, n), raw


# ---------------------------------------------------------------------------
# tbiktag's Delta-RSI Oscillator
# ---------------------------------------------------------------------------

@njit(cache=True)
def _poly_diff_nb(x, C, J, window, degree):
    diff = np.full(x.shape, NAN)
    nrmse = np.full(x.shape, NAN)
    y = np.empty(window)
    for c in range(x.shape[1]):
        for t in range(window - 1, x.shape[0]):
            ok = True
            for j in range(window):
                v = x[t - window + 1 + j, c]  # j = 0 is the oldest bar
                if np.isnan(v):
                    ok = False
                    break
                y[j] = v
            if not ok:
                continue
            a = np.zeros(degree + 1)
            for i in range(degree + 1):
                for j in range(window):
                    a[i] += C[i, j] * y[j]
            d = 0.0
            for i in range(1, degree + 1):
                d += i * a[i] * (window - 1.0) ** (i - 1)
            mse = 0.0
            for j in range(window):
                yh = 0.0
                for i in range(degree + 1):
                    yh += J[j, i] * a[i]
                mse += (y[j] - yh) ** 2 / window
            mean = y.sum() / window
            diff[t, c] = d
            nrmse[t, c] = math.sqrt(mse) / mean if mean != 0 else NAN
    return diff, nrmse


@indicator("DELTA_RSI", ["close"], ["drsi", "signal", "nrmse"])
def delta_rsi(close, rsi_length=21, window=21, degree=2, signal_length=9):
    """Delta-RSI Oscillator [tbiktag]: time derivative of a local polynomial
    least-squares fit of the RSI.

    Over the last ``window`` RSI values (x = 0..window-1, oldest first) fit a
    polynomial of ``degree``; ``drsi`` is its slope at the newest point,
    ``nrmse`` the fit's RMSE divided by the window mean, ``signal`` =
    ema(drsi, signal_length). The script solves the fit with a QR
    pseudoinverse; this uses numpy's pseudoinverse of the same Vandermonde
    matrix (identical up to rounding).
    """
    w, deg = int(window), int(degree)
    J = np.vander(np.arange(w, dtype=float), deg + 1, increasing=True)
    C = np.ascontiguousarray(np.linalg.pinv(J))
    src = rsi_2d(close, int(rsi_length))
    d, e = _poly_diff_nb(src, C, np.ascontiguousarray(J), w, deg)
    return d, k.ema_nb(d, int(signal_length)), e


# ---------------------------------------------------------------------------
# VWAP-family statistics
# ---------------------------------------------------------------------------

@indicator("ZVWAP", ["close", "volume"], ["zvwap"])
def zvwap(close, volume, length=20):
    """Z distance from VWAP [LazyBear]: (close - mean) / sqrt(sma((close - mean)^2, n)),
    mean = sum(volume*close, n) / sum(volume, n).

    As in the script, each bar's squared deviation is taken from that bar's
    own rolling VWAP.
    """
    n = int(length)
    mean = safe_div(k.sum_nb(volume * close, n), k.sum_nb(volume, n))
    sd = np.sqrt(k.sma_nb((close - mean) ** 2, n))
    return safe_div(close - mean, sd)


@njit(cache=True)
def _vw_dev_nb(x, vol, n, stdev):
    mean = np.full(x.shape, NAN)
    dev = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for t in range(n - 1, x.shape[0]):
            sw = 0.0
            sd = 0.0
            for i in range(n):
                sw += vol[t - i, c]
                sd += vol[t - i, c] * x[t - i, c]
            b = sd / sw if sw != 0 else NAN
            mean[t, c] = b
            acc = 0.0
            for i in range(n):
                d = x[t - i, c] - b
                acc += vol[t - i, c] * (d * d if stdev else abs(d))
            if sw != 0:
                dev[t, c] = math.sqrt(acc / sw) if stdev else acc / sw
    return mean, dev


@indicator("VW_DEVIATION_BANDS", ["close", "volume"],
           ["basis", "dev", "upper2", "upper3", "lower2", "lower3"])
def vw_deviation_bands(close, volume, length=60, kind="average", log_space=False):
    """BabyShark VWAP bands [GreatestUsername]: rolling volume-weighted mean of
    the last ``length`` bars with +/-2 and +/-3 deviation bands.

    ``kind="average"`` (the script's setting) uses the volume-weighted mean
    absolute deviation ``pine_vwavdev``; ``kind="stdev"`` the volume-weighted
    standard deviation ``pine_vwstdev``. Both measure deviations from the
    current bar's mean. With ``log_space`` the statistics are computed on
    log prices and the basis and bands mapped back with exp; ``dev`` is then
    in log units.
    """
    stdev = str(kind).strip().lower().startswith("st")
    src = np.log(close) if log_space else close
    m, d = _vw_dev_nb(src, volume, int(length), stdev)
    bands = [m, m + 2 * d, m + 3 * d, m - 2 * d, m - 3 * d]
    if log_space:
        bands = [np.exp(b) for b in bands]
    return bands[0], d, bands[1], bands[2], bands[3], bands[4]


@njit(cache=True)
def _wsd_nb(x, w, n):
    shape = x.shape
    outs = [np.full(shape, NAN) for _ in range(5)]
    for c in range(shape[1]):
        for t in range(n - 1, shape[0]):
            sw = 0.0
            sxw = 0.0
            for i in range(n):
                sw += w[t - i, c]
                sxw += x[t - i, c] * w[t - i, c]
            if sw == 0 or np.isnan(sw) or np.isnan(sxw):
                continue
            mean = sxw / sw
            sq = 0.0
            nz = 0
            for i in range(n):
                sq += (mean - x[t - i, c]) ** 2 * w[t - i, c]
                if w[t - i, c] != 0:
                    nz += 1
            outs[0][t, c] = mean
            den = (nz - 1) * sw / nz if nz > 0 else NAN
            if den != 0 and not np.isnan(den):
                var = sq / den
                outs[1][t, c] = var
                outs[2][t, c] = math.sqrt(var) if var >= 0 else NAN
            outs[3][t, c] = sq / sw
            outs[4][t, c] = math.sqrt(sq / sw)
    return outs[0], outs[1], outs[2], outs[3], outs[4]


@indicator("WEIGHTED_STDEV", ["close", "weight"], ["mean", "variance", "dev", "mse", "rmse"])
def weighted_stdev(close, weight, length=20):
    """Weighted mean / standard deviation over the last ``length`` bars
    [rumpypumpydumpy], ``f_weighted_sd_from_series``.

    mean = sum(x w)/sum(w); variance = SSE_w / ((n' - 1) sum(w) / n') with n'
    the number of non-zero weights (the unbiased "reliability" weighting);
    mse = SSE_w / sum(w). With ``weight=volume`` (the script's example) the
    mean is the rolling VWAP.
    """
    return _wsd_nb(close, weight, int(length))


@indicator("WEIGHTED_STDEV_LINEAR", ["close"], ["mean", "variance", "dev", "mse", "rmse"])
def weighted_stdev_linear(close, length=20):
    """``f_weighted_sd_from_arrays`` as used in the same script: linear weights
    n, n-1, ..., 1 with the newest bar weighted n (the mean is ``ta.wma``)."""
    n = int(length)
    x = close
    out = [np.full(x.shape, NAN) for _ in range(5)]
    w = np.arange(n, 0, -1, dtype=float)  # w[i] for i bars ago
    sw = w.sum()
    lag = np.stack([shift_2d(x, i) for i in range(n)])  # (n, bars, cols)
    with np.errstate(invalid="ignore"):
        mean = np.tensordot(w, lag, axes=1) / sw
        sq = np.tensordot(w, (mean[None] - lag) ** 2, axes=1)
        var = sq / ((n - 1) * sw / n) if n > 1 else np.full(x.shape, NAN)
    out[0], out[1], out[2], out[3], out[4] = mean, var, np.sqrt(var), sq / sw, np.sqrt(sq / sw)
    return tuple(out)


@njit(cache=True)
def _gauss_sd_nb(x, n):
    half = (n - 1) / 2.0
    denom = (n / 6.0) * (n / 6.0)
    w = np.empty(n)
    for i in range(n):
        d = i - half
        w[i] = math.exp(-(d * d) / (2 * denom))
    sw = w.sum()
    mid = np.full(x.shape, NAN)
    sd = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for t in range(n - 1, x.shape[0]):
            s = 0.0
            for i in range(n):
                s += x[t - i, c] * w[i]
            g = s / sw
            q = 0.0
            for i in range(n):
                dd = x[t - i, c] - g
                q += dd * dd * w[i]
            mid[t, c] = g
            sd[t, c] = math.sqrt(q / sw)
    return mid, sd


@indicator("GAUSSIAN_STDEV_CHANNEL", ["close"], ["mid", "stdev", "upper", "lower"])
def gaussian_stdev_channel(close, length=20, mult=2.0):
    """Gaussian-weighted mean and standard deviation over the last ``length``
    bars (``f_gaussian`` / ``f_gaussian_std``, strategy-specific: "Gaussian
    Channel + Stoch RSI Strategy").

    Weights exp(-(i - (n-1)/2)^2 / (2 (n/6)^2)) for i bars ago peak in the
    middle of the window, so ``mid`` lags about (n-1)/2 bars like an SMA.
    Bands are mid +/- mult x stdev. Not DonovanWall's Gaussian Channel
    (``fmz_catalog.extra.gaussian_channel``).
    """
    mid, sd = _gauss_sd_nb(close, int(length))
    return mid, sd, mid + mult * sd, mid - mult * sd


@indicator("VPCI", ["close", "volume"], ["vpci"])
def vpci(close, volume, short=5, long=20):
    """Volume Price Confirmation Indicator (Buff Dormeier, TASC July 2007).

    VPC = vwma(close, long) - sma(close, long); VPR = vwma(close, short) /
    sma(close, short); VM = sma(volume, short) / sma(volume, long);
    VPCI = VPC x VPR x VM. Dormeier's defaults are 5 / 20.
    """
    s, lg = int(short), int(long)
    vwma_l = safe_div(k.sum_nb(close * volume, lg), k.sum_nb(volume, lg))
    vwma_s = safe_div(k.sum_nb(close * volume, s), k.sum_nb(volume, s))
    vpc = vwma_l - k.sma_nb(close, lg)
    vpr = safe_div(vwma_s, k.sma_nb(close, s))
    vm = safe_div(k.sma_nb(volume, s), k.sma_nb(volume, lg))
    return vpc * vpr * vm


# ---------------------------------------------------------------------------
# VAWSI [the "VAWSI and Trend Persistance Reversal" strategy]
# ---------------------------------------------------------------------------

@njit(cache=True)
def _vawma_nb(x, vol, atr, vavg, aavg, n):
    """sum_{i=0}^{n} x[i] w_i / sum w_i, w_i = (vol[i]/vavg + atr[i]/aavg) / 2
    (n + 1 terms; vavg and aavg are the current bar's averages)."""
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for t in range(n, x.shape[0]):
            ws = 0.0
            sw = 0.0
            for i in range(n + 1):
                w = (vol[t - i, c] / vavg[t, c] + atr[t - i, c] / aavg[t, c]) / 2
                ws += x[t - i, c] * w
                sw += w
            out[t, c] = ws / sw if sw != 0 else NAN
    return out


@indicator("VAWSI", ["src", "high", "low", "close", "volume"], ["vawsi"])
def vawsi(src, high, low, close, volume, length=14):
    """VAWSI: RSI whose gains/losses are averaged with ``vawma``, a weighted
    mean whose weights are each bar's relative volume and relative true range
    (strategy-specific: "VAWSI and Trend Persistance Reversal").

    vawma(x, n) = sum_{i=0}^{n} x[i] w_i / sum w_i,
    w_i = (volume[i]/sma(volume, n) + tr[i]/sma(tr, n)) / 2.
    ``src`` is what the RSI is taken of (the strategy uses the Heikin Ashi
    close); the true range comes from the chart's high/low/close. The
    strategy feeds a per-bar length from Ehlers' dominant cycle; this takes a
    fixed ``length``.
    """
    n = int(length)
    tr = k.tr_nb(high, low, close, True)  # ta.atr(1)
    aavg = k.sma_nb(tr, n)
    vavg = k.sma_nb(volume, n)
    ch = change_2d(src)
    up = _vawma_nb(_pmax(ch, 0.0), volume, tr, vavg, aavg, n)
    dn = _vawma_nb(-_pmin(ch, 0.0), volume, tr, vavg, aavg, n)
    return 100 - safe_div(np.full(up.shape, 100.0), 1 + safe_div(up, dn))


@indicator("VAWSI_HLN", ["src", "high", "low"], ["hln"])
def vawsi_hln(src, high, low, length=14):
    """``hln`` from the same VAWSI strategy (strategy-specific): the absolute
    one-bar change of a zero-seeded Wilder average of
    max(|src - src[1]|, high - low), as a percentage of ``src``.

    The script's own ``rma`` sums a window and then overwrites it with
    ``nz(rma[1]) * (n-1)/n + x/n``, i.e. a 0-seeded Wilder MA (``WiMA``).
    A zero change gives na (``src / 0``), as in Pine.
    """
    n = float(length)
    tr = _pmax(np.abs(src - shift_2d(src, 1)), high - low)
    rm = _wima0_nb(tr, n)
    t = safe_div(src, np.abs(change_2d(rm)))
    return safe_div(np.ones(t.shape), t) * 100


# ---------------------------------------------------------------------------
# Blackflag FTS (Jose Azcarate)
# ---------------------------------------------------------------------------

@njit(cache=True)
def _blackflag_nb(high, low, close, tr, n, factor):
    shape = close.shape
    trail = np.full(shape, NAN)
    trend = np.full(shape, NAN)
    ext = np.full(shape, NAN)
    for c in range(shape[1]):
        wild = NAN
        tu1 = NAN
        td1 = NAN
        tr1 = NAN
        ex1 = NAN
        for i in range(shape[0]):
            p = 0.0 if np.isnan(wild) else wild
            wild = p + (tr[i, c] - p) / n
            loss = factor * wild
            up = close[i, c] - loss
            dn = close[i, c] + loss
            c1 = close[i - 1, c] if i > 0 else NAN
            tu = max(up, tu1) if c1 > tu1 else up  # na comparisons are false
            if c1 > tu1 and np.isnan(up):
                tu = NAN
            td = min(dn, td1) if c1 < td1 else dn
            if c1 < td1 and np.isnan(dn):
                td = NAN
            if close[i, c] > td1:
                tdir = 1.0
            elif close[i, c] < tu1:
                tdir = -1.0
            else:
                tdir = 1.0 if np.isnan(tr1) else tr1
            if tdir > 0 and tr1 <= 0:
                ex = high[i, c]
            elif tdir < 0 and tr1 >= 0:
                ex = low[i, c]
            elif tdir == 1:
                ex = NAN if np.isnan(ex1) else max(ex1, high[i, c])
            else:
                ex = NAN if np.isnan(ex1) else min(ex1, low[i, c])
            trail[i, c] = tu if tdir == 1 else td
            trend[i, c] = tdir
            ext[i, c] = ex
            tu1, td1, tr1, ex1 = tu, td, tdir, ex
    return trail, trend, ext


@indicator("BLACKFLAG_FTS", ["high", "low", "close"],
           ["trail", "trend", "extremum", "fib1", "fib2", "fib3"])
def blackflag_fts(high, low, close, trail_type="modified", atr_period=28, atr_factor=5.0):
    """Blackflag FTS (Jose Azcarate; v4 script by Duyck): ATR trailing stop
    with Fibonacci retracement entry zones (the "SwingArm").

    The "modified" true range is max(HiLo, HRef, LRef) with HiLo capped at
    1.5 x sma(high - low, n) and gap adjustments; "unmodified" is the
    classic TR. loss = factor x Wilder MA (0-seeded) of that range, the stop
    ratchets like a Supertrend, ``trend`` is +1 / -1, ``extremum`` is the
    highest high (lowest low) since the trend began (na until the first
    trend change, as in Pine), and fib1/2/3 are the 61.8 / 78.6 / 88.6 %
    retracements from the extremum towards the stop.
    """
    n = int(atr_period)
    hl = high - low
    hl_sma = k.sma_nb(hl, n)
    hilo = _pmin(hl, 1.5 * np.where(np.isnan(hl_sma), 0.0, hl_sma))
    h1, l1, c1 = shift_2d(high, 1), shift_2d(low, 1), shift_2d(close, 1)
    with np.errstate(invalid="ignore"):
        href = np.where(low <= h1, high - c1, (high - c1) - 0.5 * (low - h1))
        lref = np.where(high >= l1, c1 - low, (c1 - low) - 0.5 * (l1 - high))
    if str(trail_type).strip().lower() == "modified":
        tr = _pmax(_pmax(hilo, href), lref)
    else:
        tr = _pmax(_pmax(hl, np.abs(high - c1)), np.abs(low - c1))
    trail, trend, ex = _blackflag_nb(high, low, close, tr, float(n), float(atr_factor))
    fibs = [ex + (trail - ex) * lv / 100 for lv in (61.8, 78.6, 88.6)]
    return trail, trend, ex, fibs[0], fibs[1], fibs[2]


# ---------------------------------------------------------------------------
# Single-strategy oscillators and statistics
# ---------------------------------------------------------------------------

@indicator("RANGE_VOLATILITY", ["close"], ["volatility", "upper", "lower", "mid"])
def range_volatility(close, length=100, avg_length=100):
    """Volatility Range Breakout [wbburgin] (strategy-specific).

    volatility = 2 (highest - lowest) / (highest + lowest) of the source
    over ``length`` bars. upper/lower are the averages over ``avg_length``
    bars of close x (1 +/- volatility); the script's ``wma`` gives every bar
    the same weight (the current volatility), so it is an SMA except that a
    zero volatility gives na. ``mid`` = (upper + lower) / 2.
    """
    n, m = int(length), int(avg_length)
    hh = k.highest_nb(close, n)
    ll = k.lowest_nb(close, n)
    vx = safe_div(2 * (hh - ll), hh + ll)
    zero = vx == 0  # the script's weights are all 0 -> 0/0 = na
    up = np.where(zero, NAN, k.sma_nb(close + close * vx, m))
    lo = np.where(zero, NAN, k.sma_nb(close - close * vx, m))
    return vx, up, lo, (up + lo) / 2


@njit(cache=True)
def _vsf_nb(high, low, close, volume, session):
    shape = close.shape
    sp = np.full(shape, NAN)
    sn = np.full(shape, NAN)
    for c in range(shape[1]):
        start = 0
        for t in range(shape[0]):
            if t == 0 or session[t, c] != session[t - 1, c]:
                start = t
            a = 0.0
            b = 0.0
            for j in range(start, t):  # bars 1 .. L-1 back: earlier bars of this session
                rng = high[j, c] - low[j, c]
                if rng == 0 or np.isnan(rng):
                    a = NAN
                    b = NAN
                    break
                a += volume[j, c] * ((close[j, c] - low[j, c]) / rng * 100) / 100
                b += volume[j, c] * ((high[j, c] - close[j, c]) / rng * 100) / 100
            sp[t, c] = a
            sn[t, c] = b
    return sp, sn


@indicator("VOLUME_STRENGTH", ["high", "low", "close", "volume", "session"], ["sspv", "ssnv", "pos", "neg"])
def volume_strength(high, low, close, volume, session):
    """Volume Strength Finder [Saravanan_Ragavan] (strategy-specific).

    Over the earlier bars of the current session (not the current bar), each
    bar's volume is split by where it closed in its range:
    sspv += volume x (close - low)/(high - low), ssnv += volume x
    (high - close)/(high - low). pos/neg = 100 x sspv/ssnv over their sum.
    ``session`` is a session id per bar (e.g. ``ti.session_ids(index, "D")``);
    the script anchors at its 09:15 bar. A flat bar in the session gives na
    (division by zero), as in Pine. On the first bar of a session the sums
    are empty (pos/neg na); the script's ``for i = 1 to L - 1`` runs
    backwards there and adds the previous session's last bar and the current
    bar instead.
    """
    sp, sn = _vsf_nb(high, low, close, volume, session)
    tot = sp + sn
    return sp, sn, 100 * safe_div(sp, tot), 100 * safe_div(sn, tot)


@njit(cache=True)
def _count_vs_lag_nb(x, ref, start, end):
    """sum over i = start..end of sign(x[t] - ref[t-i]); na comparisons count 0."""
    out = np.zeros(x.shape)
    for c in range(x.shape[1]):
        for t in range(x.shape[0]):
            s = 0.0
            for i in range(start, end + 1):
                if t - i < 0:
                    continue
                r = ref[t - i, c]
                if x[t, c] > r:
                    s += 1
                elif x[t, c] < r:
                    s -= 1
            out[t, c] = s
    return out


@indicator("TMO", ["open", "close"], ["main", "signal", "raw"])
def tmo(open, close, length=14, calc_length=5, smooth_length=3, start=0):
    """True Momentum Oscillator (Mobius, thinkorswim 2018).

    raw = sum over i = start..length-1 of sign(close - open[i]) (Mobius'
    ``fold i = 0 to length``); main = ema(ema(raw, calc_length),
    smooth_length); signal = ema(main, smooth_length). OB/OS levels are
    +/- round(0.7 x length). Uses ``ta.ema`` (SMA seed) like the Pine ports.
    ``start=1`` reproduces the ``for i = 1 to tmolength-1`` loop of the FMZ
    "15MIN BTCUSDTPERP BOT" copy, which skips the current bar's open.
    """
    raw = _count_vs_lag_nb(close, open, int(start), int(length) - 1)
    e5 = k.ema_nb(raw, int(calc_length))
    main = k.ema_nb(e5, int(smooth_length))
    return main, k.ema_nb(main, int(smooth_length)), raw


@indicator("FOR_LOOP_SCORE", ["close"], ["score"])
def for_loop_score(close, start=1, end=50):
    """"For-loop" trend score: +1 for every lag i in start..end where the
    series is above its value i bars ago, -1 where below (the
    ``forloop_analysis`` of the Zero Lag Trend Strategy, applied there to a
    zero-lag EMA). Lags beyond the history count 0, as Pine's na compare."""
    return _count_vs_lag_nb(close, close, int(start), int(end))


@njit(cache=True)
def _friction_nb(high, low, close, bb):
    out = np.zeros(close.shape)
    for c in range(close.shape[1]):
        for t in range(close.shape[0]):
            f = 0.0
            for i in range(1, min(bb, t) + 1):
                if high[t - i, c] >= close[t, c] and low[t - i, c] <= close[t, c]:
                    f += (1.0 + bb) / (i + bb)
            out[t, c] = f
    return out


@indicator("PRICE_FRICTION", ["high", "low", "close"], ["friction", "low_f", "high_f", "mid_f", "trigger"])
def price_friction(high, low, close, barsback=500, range_length=100, flevel=50.0, tlevel=-10.0):
    """"LUBE" price friction (strategy-specific).

    friction = sum over the previous ``barsback`` bars whose high-low range
    contains the current close of (1 + barsback) / (i + barsback). low_f /
    high_f are its lowest / highest over ``range_length`` bars, mid_f =
    low_f + (high_f - low_f) x flevel/100 and trigger = low_f + (high_f -
    low_f) x tlevel/100. The strategy compares friction with ``mid_f[5]`` and
    ``trigger[5]``.
    """
    bb = int(barsback)
    f = _friction_nb(high, low, close, bb)
    r = int(range_length)
    lo = k.lowest_nb(f, r)
    hi = k.highest_nb(f, r)
    fl, tl = flevel / 100.0, tlevel / 100.0
    return f, lo, hi, lo * (1 - fl) + hi * fl, lo * (1 - tl) + hi * tl


@njit(cache=True)
def _harsi_open_nb(o_rsi, c_rsi, ha_c, s):
    out = np.full(o_rsi.shape, NAN)
    for c in range(o_rsi.shape[1]):
        for t in range(o_rsi.shape[0]):
            back = out[t - s, c] if t >= s else NAN
            if np.isnan(back):
                out[t, c] = (o_rsi[t, c] + c_rsi[t, c]) / 2
            else:
                out[t, c] = (out[t - 1, c] * s + ha_c[t - 1, c]) / (s + 1)
    return out


@indicator("RSI_HEIKIN_ASHI", ["high", "low", "close"], ["open", "high", "low", "close"])
def rsi_heikin_ashi(high, low, close, length=14, smoothing=1):
    """Heikin Ashi RSI Oscillator [JayRogers] (``f_rsiHeikinAshi``).

    Zero-centred RSIs (rsi - 50) of close, high and low form a candle whose
    open is the previous RSI close; it is then Heikin-Ashi-ed with an open
    smoothed by ``smoothing`` (1 in the original, 7 in the FMZ strategy):
    open = (open[1] x s + close[1]) / (s + 1).
    """
    n, s = int(length), int(smoothing)
    c_rsi = rsi_2d(close, n) - 50
    o_rsi = shift_2d(c_rsi, 1)
    o_rsi = np.where(np.isnan(o_rsi), c_rsi, o_rsi)
    hr, lr = rsi_2d(high, n) - 50, rsi_2d(low, n) - 50
    h_rsi, l_rsi = _pmax(hr, lr), _pmin(hr, lr)
    ha_c = (o_rsi + h_rsi + l_rsi + c_rsi) / 4
    ha_o = _harsi_open_nb(o_rsi, c_rsi, ha_c, s)
    return ha_o, _pmax(h_rsi, _pmax(ha_o, ha_c)), _pmin(l_rsi, _pmin(ha_o, ha_c)), ha_c


@indicator("RELATIVE_BODY_INDEX", ["open", "high", "low", "close"], ["rbi", "signal"])
def relative_body_index(open, high, low, close, length=5, signal_length=5, binary=False):
    """Relative Body Index [Vitelot] (strategy-specific): ema(sum(rb, n), n)
    with rb = (close - open) / (high - low) (``binary``: +1 for a bull
    candle, -1 otherwise); ``signal`` = ema(rbi, signal_length)."""
    n = int(length)
    if binary:
        s = np.where(_gt(close, open), 1.0, -1.0)
    else:
        s = safe_div(close - open, high - low)
    yn = k.ema_nb(k.sum_nb(s, n), n)
    return yn, k.ema_nb(yn, int(signal_length))


@njit(cache=True)
def _hurst_nb(r, n):
    out = np.full(r.shape, NAN)
    for c in range(r.shape[1]):
        for t in range(n - 1, r.shape[0]):
            m = 0.0
            ok = True
            for i in range(n):
                v = r[t - n + 1 + i, c]
                if np.isnan(v):
                    ok = False
                    break
                m += v
            if not ok:
                continue
            m /= n
            y = 0.0
            ymax = 0.0
            ymin = 0.0
            ss = 0.0
            for i in range(n):
                d = r[t - n + 1 + i, c] - m  # oldest first
                y += d
                ss += d * d
                if y > ymax:
                    ymax = y
                if y < ymin:
                    ymin = y
            s = math.sqrt(ss / n)
            rr = ymax - ymin
            if s > 0 and rr > 0:
                out[t, c] = math.log(rr / s) / math.log(n)
    return out


@indicator("HURST_EXPONENT", ["close"], ["hurst"])
def hurst_exponent(close, length=50):
    """Hurst exponent from the rescaled range of the last ``length`` log
    returns (Hurst 1951, single-window estimate): H = log(R/S) / log(n),
    R = range of the cumulative deviations from the window's mean return,
    S = their population stdev.

    The single-window estimate is biased upward for small n (about 0.6 for
    a random walk at n = 50); compare it with its own history rather than
    with 0.5 exactly.
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.log(close / shift_2d(close, 1))
    return _hurst_nb(r, int(length))


@njit(cache=True)
def _weis_nb(close, volume, rising, falling):
    shape = close.shape
    wave_o = np.full(shape, NAN)
    vol_o = np.full(shape, NAN)
    for c in range(shape[1]):
        trend1 = NAN
        wave1 = NAN
        vol1 = NAN
        mov1 = NAN
        for i in range(shape[0]):
            p = close[i - 1, c] if i > 0 else NAN
            mov = 1.0 if close[i, c] > p else (-1.0 if close[i, c] < p else 0.0)
            tr = mov if (mov != 0 and not np.isnan(mov1) and mov != mov1) else (0.0 if np.isnan(trend1) else trend1)
            w1 = 0.0 if np.isnan(wave1) else wave1
            wave = tr if (tr != w1 and (rising[i, c] or falling[i, c])) else w1
            if not np.isnan(wave1) and wave == wave1:
                vol = (0.0 if np.isnan(vol1) else vol1) + volume[i, c]
            else:
                vol = volume[i, c]
            wave_o[i, c] = wave
            vol_o[i, c] = vol
            trend1, wave1, vol1, mov1 = tr, wave, vol, mov
    return wave_o, vol_o


def _rising_falling(x, n):
    r = np.ones(x.shape, dtype=bool)
    f = np.ones(x.shape, dtype=bool)
    for j in range(1, n + 1):
        p = shift_2d(x, j)
        r &= _gt(x, p)
        f &= _lt(x, p)
    return r, f


@indicator("WEIS_WAVE_VOLUME", ["close", "volume"], ["wave", "wave_volume", "up", "down"])
def weis_wave_volume(close, volume, length=2, below_zero=True):
    """Weis Wave Volume [LazyBear]: volume accumulated over each wave.

    A new wave starts when the close direction flips and the close is
    rising/falling over ``length`` bars (``trendDetectionLength``, 2 in the
    original). ``up`` is the wave volume of up waves, ``down`` of down waves
    (negative when ``below_zero``, as the script's default plot).
    """
    r, f = _rising_falling(close, int(length))
    wave, vol = _weis_nb(close, volume, r, f)
    up = np.where(wave == 1, vol, 0.0)
    if below_zero:
        dn = np.where(wave == 1, 0.0, np.where(wave == -1, -vol, vol))
    else:
        dn = np.where(wave == 1, 0.0, vol)
    return wave, vol, up, dn


@indicator("FAYTTERRO_ESTIMATOR", ["close"], ["estimator", "forecast", "buy", "sell"])
def faytterro_estimator(close, length=10):
    """Faytterro Estimator strategy core [faytterro] (strategy-specific).

    ``estimator`` = triangular-weighted mean over 2n-1 bars (peak weight n,
    normalised by n^2), i.e. ``ti.trima(src, 2n - 1)``; the script passes
    hlc3. ``forecast`` is the quadratic through estimator[2], [1], [0]
    extrapolated n+4 bars ahead (``dizi[len+6]``); ``buy`` / ``sell`` are the
    raw turn signals before the strategy's price-gap filters: the forecast
    rising (falling) and below (above) estimator[n]. For n < 6 the script
    reads past its array and never signals.
    """
    n = int(length)
    y = 2 * n - 1
    w = np.array([(y - 1) / 2 + 1 - abs(i - (y - 1) / 2) for i in range(y)])
    lag = np.stack([shift_2d(close, i) for i in range(y)])
    cr = np.tensordot(w, lag, axes=1) / (((y + 1) / 2) * (y + 1) / 2)
    c1, c2 = shift_2d(cr, 1), shift_2d(cr, 2)

    def quad(i):
        return i * (i - 1) * (cr - 2 * c1 + c2) / 2 + i * (c1 - c2) + c2

    if n + 6 > 2 * n:
        f = np.full(cr.shape, NAN)
        return cr, f, np.zeros(cr.shape, bool), np.zeros(cr.shape, bool)
    f6, f5 = quad(n + 6), quad(n + 5)
    cn = shift_2d(cr, n)
    return cr, f6, _gt(f6, f5) & _lt(f6, cn), _lt(f6, f5) & _gt(f6, cn)


@njit(cache=True)
def _gyro_nb(close, vara, varb):
    shape = close.shape
    pos_o = np.full(shape, NAN)
    traj_o = np.full(shape, NAN)
    for c in range(shape[1]):
        pos1 = NAN
        traj1 = NAN
        for i in range(shape[0]):
            cl = close[i, c]
            c1 = close[i - 1, c] if i > 0 else NAN
            c2 = close[i - 2, c] if i > 1 else NAN
            nz1 = 0.0 if np.isnan(c1) else c1
            nz2 = 0.0 if np.isnan(c2) else c2
            tr = (nz1 - nz2 + (0.0 if np.isnan(traj1) else traj1) * varb) / (varb + 1)
            grav = 1.0 / math.sqrt(cl * cl) * vara
            p1 = 0.0 if np.isnan(pos1) else pos1
            seed = cl if i + 1 <= 5 else p1
            pos = p1 + grav + tr if seed < cl else p1 - grav + tr
            pos_o[i, c] = pos
            traj_o[i, c] = tr
            pos1, traj1 = pos, tr
    return pos_o, traj_o


@indicator("GYROSCOPIC_BANDS", ["close"], ["pos", "upper", "lower", "traj"])
def gyroscopic_bands(close, a_exp=4.0, b=12):
    """Jomy's Gyroscopic Bands (strategy-specific).

    traj = (close[1] - close[2] + traj[1] x b) / (b + 1) (a smoothed lagged
    change, ``nz``-seeded); pos steps by +/- 10^a_exp / close towards the
    close plus traj; bands = pos +/- sma(|close - pos|, b). Ported bar for
    bar: the script's "pos = close for the first 5 bars" seed is overwritten
    on the same bar, so pos starts near 0 and reaches the price only through
    the one-off ``close[1] - nz(close[2])`` = close jump in traj at bar 1
    (it decays with factor b/(b+1)); discard the first several x b bars.
    """
    pos, traj = _gyro_nb(close, float(10.0 ** a_exp), float(b))
    dist = k.sma_nb(np.abs(close - pos), int(b))
    return pos, pos + dist, pos - dist, traj


# ---------------------------------------------------------------------------
# Rolling volume profile and the buy/sell volume heatmap
# ---------------------------------------------------------------------------

@njit(cache=True)
def _vp_nb(high, low, volume, n, rows, va):
    shape = high.shape
    poc = np.full(shape, NAN)
    vah = np.full(shape, NAN)
    val = np.full(shape, NAN)
    hist = np.zeros(rows)
    for c in range(shape[1]):
        for t in range(n - 1, shape[0]):
            ok = True
            hi = -np.inf
            lo = np.inf
            for j in range(t - n + 1, t + 1):
                if np.isnan(high[j, c]) or np.isnan(low[j, c]) or np.isnan(volume[j, c]):
                    ok = False
                    break
                hi = max(hi, high[j, c])
                lo = min(lo, low[j, c])
            if not ok:
                continue
            if hi <= lo:
                poc[t, c] = hi
                vah[t, c] = hi
                val[t, c] = hi
                continue
            step = (hi - lo) / rows
            hist[:] = 0.0
            for j in range(t - n + 1, t + 1):
                hj, lj, vj = high[j, c], low[j, c], volume[j, c]
                if hj <= lj:
                    r = min(int((hj - lo) / step), rows - 1)
                    hist[r] += vj
                    continue
                r0 = min(int((lj - lo) / step), rows - 1)
                r1 = min(int((hj - lo) / step), rows - 1)
                for r in range(r0, r1 + 1):
                    bot = lo + r * step
                    top = hi if r == rows - 1 else bot + step
                    ov = min(hj, top) - max(lj, bot)
                    if ov > 0:
                        hist[r] += vj * ov / (hj - lj)
            p = 0
            for r in range(1, rows):
                if hist[r] > hist[p]:
                    p = r
            remaining = hist.sum() * va / 100.0 - hist[p]
            up = p + 1
            dn = p - 1
            while up < rows or dn >= 0:
                if up < rows and dn >= 0:
                    if hist[up] > hist[dn]:
                        take_up = True
                    elif hist[dn] > hist[up]:
                        take_up = False
                    else:  # tie: closer to the POC, then the upper row
                        take_up = (up - p) <= (p - dn)
                else:
                    take_up = up < rows
                vol = hist[up] if take_up else hist[dn]
                if vol > remaining:
                    break
                remaining -= vol
                if take_up:
                    up += 1
                else:
                    dn -= 1
            poc[t, c] = lo + (p + 0.5) * step
            vah[t, c] = lo + up * step
            val[t, c] = lo + (dn + 1) * step
    return poc, vah, val


@indicator("VOLUME_PROFILE", ["high", "low", "volume"], ["poc", "vah", "val"])
def volume_profile(high, low, volume, length=100, rows=24, value_area=70.0):
    """Rolling volume profile of the last ``length`` bars (current bar
    included, nothing later): Point of Control and Value Area High / Low.

    The window's [lowest low, highest high] is split into ``rows`` equal
    rows and each bar's volume is spread uniformly over its high-low range
    (a flat bar puts it all in one row); TradingView builds its profile from
    lower-timeframe bars instead. ``poc`` is the middle of the row with the
    most volume (lowest such row on ties). The value area follows
    TradingView's procedure: from the POC, repeatedly compare the next row
    above and below, take the larger (ties: closer to the POC, then above),
    and stop before the area would exceed ``value_area`` % of the volume.
    ``vah`` / ``val`` are the top / bottom edges of the area's outer rows.
    Recomputed from scratch every bar, so it never repaints.
    """
    return _vp_nb(high, low, volume, int(length), int(rows), float(value_area))


@njit(cache=True)
def _heatmap_nb(open_, high, low, close, volume, lookback, levels, pct):
    shape = close.shape
    buy = np.full(shape, NAN)
    sell = np.full(shape, NAN)
    for c in range(shape[1]):
        for t in range(shape[0]):
            bsum = 0.0
            ssum = 0.0
            for lv in range(levels):
                level = close[t, c] * (1 + (lv - levels / 2.0) * pct)
                for j in range(1, lookback + 1):
                    if t - j < 0:
                        continue  # na history: every comparison is false
                    cj, oj = close[t - j, c], open_[t - j, c]
                    if cj > oj:
                        if cj >= level and low[t - j, c] <= level:
                            bsum += volume[t - j, c]
                    elif cj <= level and high[t - j, c] >= level:
                        ssum += volume[t - j, c]
            buy[t, c] = bsum
            sell[t, c] = ssum
    return buy, sell


@indicator("VOLUME_HEATMAP", ["open", "high", "low", "close", "volume"], ["buy", "sell"])
def volume_heatmap(open, high, low, close, volume, lookback=100, levels=10, range_pct=0.01):
    """"Buy and Sell Volume Heatmap" totals (strategy-specific).

    ``levels`` prices close x (1 + (i - levels/2) x range_pct) around the
    current close; for each, the volume of the previous ``lookback`` bars
    (current bar excluded) whose close-to-low (bull bars) or close-to-high
    (other bars) span contains the level is added to ``buy`` / ``sell``.
    The strategy only colours labels with buy > sell.
    """
    return _heatmap_nb(open, high, low, close, volume, int(lookback), int(levels), float(range_pct))


# Keep these out of tv_indicators' registry so the main library is unchanged.
EXTRA_MISC = {name: REGISTRY.pop(name) for name in list(REGISTRY) if name not in _BEFORE}

__all__ = sorted(fn.__name__ for fn in EXTRA_MISC.values())
