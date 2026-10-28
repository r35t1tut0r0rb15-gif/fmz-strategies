"""Popular TradingView community scripts (trend filters, trailing stops, QQE, STC...).

Each one follows the published Pine source of the script named in its
docstring, including the script's own warm-up behaviour.
"""

import numpy as np
from numba import njit

from . import kernels as k
from ._core import change_2d, indicator, safe_div, shift_2d
from .oscillators import mfi as _mfi, rsi_2d
from .volatility import atr_2d

NAN = np.nan
_max2, _min2, _nz = k._max2, k._min2, k._nz


# ---------------------------------------------------------------------------
# Kernels
# ---------------------------------------------------------------------------

@njit(cache=True)
def _st_kivanc_nb(src, close, atr, mult):
    shape = src.shape
    st = np.full(shape, NAN)
    tr_out = np.full(shape, NAN)
    up_o = np.full(shape, NAN)
    dn_o = np.full(shape, NAN)
    for c in range(shape[1]):
        prev_up = NAN
        prev_dn = NAN
        trend = 1.0
        for i in range(shape[0]):
            up = src[i, c] - mult * atr[i, c]
            up1 = up if np.isnan(prev_up) else prev_up
            c1 = close[i - 1, c] if i > 0 else NAN
            if c1 > up1:
                up = _max2(up, up1)
            dn = src[i, c] + mult * atr[i, c]
            dn1 = dn if np.isnan(prev_dn) else prev_dn
            if c1 < dn1:
                dn = _min2(dn, dn1)
            if trend == -1.0 and close[i, c] > dn1:
                trend = 1.0
            elif trend == 1.0 and close[i, c] < up1:
                trend = -1.0
            up_o[i, c] = up
            dn_o[i, c] = dn
            tr_out[i, c] = trend
            st[i, c] = up if trend == 1.0 else dn
            prev_up = up
            prev_dn = dn
    return st, tr_out, up_o, dn_o


@njit(cache=True)
def _halftrend_nb(high, low, close, high_price, low_price, highma, lowma, atr2, dev):
    shape = close.shape
    ht = np.full(shape, NAN)
    trend_o = np.full(shape, NAN)
    ah = np.full(shape, NAN)
    al = np.full(shape, NAN)
    buy = np.zeros(shape, dtype=np.bool_)
    sell = np.zeros(shape, dtype=np.bool_)
    for c in range(shape[1]):
        trend = 0
        next_trend = 0
        max_low = low[0, c]
        min_high = high[0, c]
        up = 0.0
        down = 0.0
        prev_trend = -1  # -1 stands for na
        for i in range(shape[0]):
            pl = low[i - 1, c] if i > 0 else low[i, c]
            ph = high[i - 1, c] if i > 0 else high[i, c]
            if next_trend == 1:
                if not np.isnan(low_price[i, c]):
                    max_low = max(low_price[i, c], max_low)
                if highma[i, c] < max_low and close[i, c] < pl:
                    trend = 1
                    next_trend = 0
                    min_high = high_price[i, c]
            else:
                if not np.isnan(high_price[i, c]):
                    min_high = min(high_price[i, c], min_high)
                if lowma[i, c] > min_high and close[i, c] > ph:
                    trend = 0
                    next_trend = 1
                    max_low = low_price[i, c]
            first = i == 0
            arrow_up = NAN
            arrow_down = NAN
            if trend == 0:
                if prev_trend != -1 and prev_trend != 0:
                    up = down
                    arrow_up = up - atr2[i, c]
                else:
                    up = max_low if first else _max2(max_low, up)
                ah[i, c] = up + dev[i, c]
                al[i, c] = up - dev[i, c]
            else:
                if prev_trend != -1 and prev_trend != 1:
                    down = up
                    arrow_down = down + atr2[i, c]
                else:
                    down = min_high if first else _min2(min_high, down)
                ah[i, c] = down + dev[i, c]
                al[i, c] = down - dev[i, c]
            ht[i, c] = up if trend == 0 else down
            trend_o[i, c] = trend
            buy[i, c] = (not np.isnan(arrow_up)) and trend == 0 and prev_trend == 1
            sell[i, c] = (not np.isnan(arrow_down)) and trend == 1 and prev_trend == 0
            prev_trend = trend
    return ht, trend_o, ah, al, buy, sell


@njit(cache=True)
def _ssl_nb(close, sma_high, sma_low):
    shape = close.shape
    up_o = np.full(shape, NAN)
    dn_o = np.full(shape, NAN)
    hlv_o = np.full(shape, NAN)
    for c in range(shape[1]):
        hlv = NAN
        for i in range(shape[0]):
            if close[i, c] > sma_high[i, c]:
                hlv = 1.0
            elif close[i, c] < sma_low[i, c]:
                hlv = -1.0
            hlv_o[i, c] = hlv
            if hlv < 0:
                dn_o[i, c] = sma_high[i, c]
                up_o[i, c] = sma_low[i, c]
            else:
                dn_o[i, c] = sma_low[i, c]
                up_o[i, c] = sma_high[i, c]
    return up_o, dn_o, hlv_o


@njit(cache=True)
def _range_filter_nb(src, rng):
    shape = src.shape
    filt = np.full(shape, NAN)
    up_o = np.zeros(shape)
    dn_o = np.zeros(shape)
    ini_o = np.full(shape, NAN)
    buy = np.zeros(shape, dtype=np.bool_)
    sell = np.zeros(shape, dtype=np.bool_)
    for c in range(shape[1]):
        prev_f = NAN
        upward = 0.0
        downward = 0.0
        ini = NAN
        for i in range(shape[0]):
            x = src[i, c]
            r = rng[i, c]
            p = _nz(prev_f)
            if x > p:
                f = p if x - r < p else x - r
            else:
                f = p if x + r > p else x + r
            if f > prev_f:
                upward = upward + 1
            elif f < prev_f:
                upward = 0.0
            if f < prev_f:
                downward = downward + 1
            elif f > prev_f:
                downward = 0.0
            s1 = src[i - 1, c] if i > 0 else NAN
            long_c = (x > f and x > s1 and upward > 0) or (x > f and x < s1 and upward > 0)
            short_c = (x < f and x < s1 and downward > 0) or (x < f and x > s1 and downward > 0)
            prev_ini = ini
            if long_c:
                ini = 1.0
            elif short_c:
                ini = -1.0
            filt[i, c] = f
            up_o[i, c] = upward
            dn_o[i, c] = downward
            ini_o[i, c] = ini
            buy[i, c] = long_c and prev_ini == -1.0
            sell[i, c] = short_c and prev_ini == 1.0
            prev_f = f
    return filt, up_o, dn_o, ini_o, buy, sell


@njit(cache=True)
def _atr_flip_nb(bull, low, high, atr, coeff):
    """Shared recursion of Trend Magic and AlphaTrend."""
    out = np.full(low.shape, NAN)
    for c in range(low.shape[1]):
        prev = NAN
        for i in range(low.shape[0]):
            p = _nz(prev)
            if bull[i, c]:
                up = low[i, c] - atr[i, c] * coeff
                v = p if up < p else up
            else:
                dn = high[i, c] + atr[i, c] * coeff
                v = p if dn > p else dn
            out[i, c] = v
            prev = v
    return out


@njit(cache=True)
def _ott_nb(mavg, percent):
    shape = mavg.shape
    ott = np.full(shape, NAN)
    mt_o = np.full(shape, NAN)
    dir_o = np.full(shape, NAN)
    for c in range(shape[1]):
        prev_ls = NAN
        prev_ss = NAN
        d = 1.0
        for i in range(shape[0]):
            m = mavg[i, c]
            fark = m * percent * 0.01
            ls = m - fark
            lsp = ls if np.isnan(prev_ls) else prev_ls
            if m > lsp:
                ls = _max2(ls, lsp)
            ss = m + fark
            ssp = ss if np.isnan(prev_ss) else prev_ss
            if m < ssp:
                ss = _min2(ss, ssp)
            if d == -1.0 and m > ssp:
                d = 1.0
            elif d == 1.0 and m < lsp:
                d = -1.0
            mt = ls if d == 1.0 else ss
            ott[i, c] = mt * (200 + percent) / 200 if m > mt else mt * (200 - percent) / 200
            mt_o[i, c] = mt
            dir_o[i, c] = d
            prev_ls = ls
            prev_ss = ss
    return ott, mt_o, dir_o


@njit(cache=True)
def _cross(a, b, a1, b1):
    return (a > b and a1 <= b1) or (a < b and a1 >= b1)


@njit(cache=True)
def _qqe_nb(rsi_ma, dar):
    shape = rsi_ma.shape
    lb_o = np.full(shape, NAN)
    sb_o = np.full(shape, NAN)
    tr_o = np.full(shape, NAN)
    tl_o = np.full(shape, NAN)
    for c in range(shape[1]):
        trend = NAN
        for i in range(shape[0]):
            r = rsi_ma[i, c]
            r1 = rsi_ma[i - 1, c] if i > 0 else NAN
            plb = lb_o[i - 1, c] if i > 0 else NAN
            psb = sb_o[i - 1, c] if i > 0 else NAN
            plb2 = lb_o[i - 2, c] if i > 1 else NAN
            psb2 = sb_o[i - 2, c] if i > 1 else NAN
            nlb = r - dar[i, c]
            nsb = r + dar[i, c]
            lb = _max2(plb, nlb) if (r1 > plb and r > plb) else nlb
            sb = _min2(psb, nsb) if (r1 < psb and r < psb) else nsb
            if _cross(r, psb, r1, psb2):
                trend = 1.0
            elif _cross(plb, r, plb2, r1):
                trend = -1.0
            elif np.isnan(trend):
                trend = 1.0
            lb_o[i, c] = lb
            sb_o[i, c] = sb
            tr_o[i, c] = trend
            tl_o[i, c] = lb if trend == 1.0 else sb
    return tl_o, tr_o, lb_o, sb_o


@njit(cache=True)
def _stc_nb(macd, lo, hi, n, factor):
    shape = macd.shape
    out = np.full(shape, NAN)
    ddd_hist = np.full(shape, NAN)
    for c in range(shape[1]):
        c5 = 0.0
        ddd = NAN
        d6 = 0.0
        e5 = NAN
        for i in range(shape[0]):
            rng = hi[i, c] - lo[i, c]
            if rng > 0:
                c5 = (macd[i, c] - lo[i, c]) / rng * 100
            ddd = c5 if np.isnan(ddd) else ddd + factor * (c5 - ddd)
            ddd_hist[i, c] = ddd
            if i >= n - 1:
                dl = ddd_hist[i, c]
                dh = ddd_hist[i, c]
                for j in range(1, n):
                    v = ddd_hist[i - j, c]
                    dl = min(dl, v)
                    dh = max(dh, v)
                if dh - dl > 0:
                    d6 = (ddd - dl) / (dh - dl) * 100
            e5 = d6 if np.isnan(e5) else e5 + factor * (d6 - e5)
            out[i, c] = e5
    return out


@njit(cache=True)
def _vstop_nb(src, atr_m, tr):
    shape = src.shape
    stop_o = np.full(shape, NAN)
    up_o = np.full(shape, NAN)
    for c in range(shape[1]):
        mx = src[0, c]
        mn = src[0, c]
        uptrend = True
        stop = NAN
        for i in range(shape[0]):
            a = atr_m[i, c] if not np.isnan(atr_m[i, c]) else tr[i, c]
            mx = max(mx, src[i, c])
            mn = min(mn, src[i, c])
            cand = _max2(stop, mx - a) if uptrend else _min2(stop, mn + a)
            stop = src[i, c] if np.isnan(cand) else cand
            new_up = src[i, c] - stop >= 0.0
            if new_up != uptrend:
                mx = src[i, c]
                mn = src[i, c]
                stop = mx - a if new_up else mn + a
            uptrend = new_up
            stop_o[i, c] = stop
            up_o[i, c] = 1.0 if uptrend else -1.0
    return stop_o, up_o


def _crossover(a, b):
    a1, b1 = shift_2d(a, 1), shift_2d(b, 1)
    with np.errstate(invalid="ignore"):
        return (a > b) & (a1 <= b1)


def _crossunder(a, b):
    return _crossover(b, a)


# ---------------------------------------------------------------------------
# Indicators
# ---------------------------------------------------------------------------

@indicator("SUPERTREND_KIVANC", ["high", "low", "close"], ["supertrend", "trend", "up", "dn", "buy", "sell"])
def supertrend_kivanc(high, low, close, period=10, multiplier=3.0, change_atr=True):
    """SuperTrend [KivancOzbilgic], TradingView's most-liked Supertrend.

    Differs from ``ta.supertrend``: the flip test uses the previous bar's
    bands. ``trend`` is 1 up / -1 down. ``change_atr=False`` uses sma(tr).
    """
    n = int(period)
    src = (high + low) / 2
    a = atr_2d(high, low, close, n) if change_atr else k.sma_nb(k.tr_nb(high, low, close, False), n)
    st, tr_, up, dn = _st_kivanc_nb(src, close, a, float(multiplier))
    prev = shift_2d(tr_, 1)
    return st, tr_, up, dn, (tr_ == 1) & (prev == -1), (tr_ == -1) & (prev == 1)


@indicator("HALFTREND", ["high", "low", "close"],
           ["halftrend", "trend", "atr_high", "atr_low", "buy", "sell"])
def halftrend(high, low, close, amplitude=2, channel_deviation=2.0):
    """HalfTrend [everget]. ``trend`` is 0 for up, 1 for down (as the script).

    The script's first bar is ill-defined in Pine (``math.max`` with na);
    here the partial window is skipped, so only the very start can differ.
    """
    amp = int(amplitude)
    atr2 = atr_2d(high, low, close, 100) / 2
    return _halftrend_nb(high, low, close, k.highest_nb(high, amp), k.lowest_nb(low, amp),
                         k.sma_nb(high, amp), k.sma_nb(low, amp), atr2, channel_deviation * atr2)


@indicator("SSL_CHANNEL", ["high", "low", "close"], ["ssl_up", "ssl_down", "hlv"])
def ssl_channel(high, low, close, length=10):
    """SSL Channel [ErwinBeckers]: SMA(high) / SMA(low) swapped by trend."""
    n = int(length)
    return _ssl_nb(close, k.sma_nb(high, n), k.sma_nb(low, n))


def _smooth_range(src, t, m):
    avrng = k.ema_nb(np.abs(change_2d(src)), int(t))
    return k.ema_nb(avrng, int(t) * 2 - 1) * m


@indicator("RANGE_FILTER", ["close"],
           ["filter", "hband", "lband", "upward", "downward", "state", "buy", "sell"])
def range_filter(close, period=100, multiplier=3.0):
    """Range Filter Buy and Sell [guikroth] (from DonovanWall's Range Filter)."""
    r = _smooth_range(close, period, multiplier)
    f, up, dn, ini, buy, sell = _range_filter_nb(close, r)
    return f, f + r, f - r, up, dn, ini, buy, sell


@indicator("TWIN_RANGE_FILTER", ["close"], ["filter", "state", "buy", "sell"])
def twin_range_filter(close, fast_period=27, fast_range=1.6, slow_period=55, slow_range=2.0):
    """Twin Range Filter [colinmck]: Range Filter on the mean of two ranges."""
    r = (_smooth_range(close, fast_period, fast_range) + _smooth_range(close, slow_period, slow_range)) / 2
    f, _, _, ini, buy, sell = _range_filter_nb(close, r)
    return f, ini, buy, sell


@indicator("TREND_MAGIC", ["high", "low", "close"], ["magic_trend", "bullish"])
def trend_magic(high, low, close, cci_period=20, atr_multiplier=1.0, atr_period=5):
    """Trend Magic [KivancOzbilgic], the most-liked version: ATR trail flipped by CCI >= 0.

    Like the script, the line sits at 0 until the first bullish bar. glaz's
    older "Trend Magic" handles CCI sign changes differently and is not this.
    """
    n = int(cci_period)
    cci = safe_div(close - k.sma_nb(close, n), 0.015 * k.dev_nb(close, n))
    a = k.sma_nb(k.tr_nb(high, low, close, False), int(atr_period))
    with np.errstate(invalid="ignore"):
        bull = cci >= 0
    return _atr_flip_nb(bull, low, high, a, float(atr_multiplier)), bull


@indicator("ALPHATREND", ["high", "low", "close", "volume"],
           ["alphatrend", "alphatrend_lag2", "buy", "sell", "buy_raw", "sell_raw"])
def alphatrend(high, low, close, volume, coeff=1.0, period=14, use_rsi=False):
    """AlphaTrend [KivancOzbilgic]: ATR trail flipped by MFI >= 50 (RSI if no volume).

    ``buy_raw``/``sell_raw`` = crossover/crossunder of AlphaTrend with its
    2-bar lag; ``buy``/``sell`` keep only alternating signals, as plotted.
    """
    n = int(period)
    a = k.sma_nb(k.tr_nb(high, low, close, False), n)
    osc = rsi_2d(close, n) if use_rsi else _mfi.core(high, low, close, volume, n)
    with np.errstate(invalid="ignore"):
        bull = osc >= 50
    at = _atr_flip_nb(bull, low, high, a, float(coeff))
    lag2 = shift_2d(at, 2)
    buy_k, sell_k = _crossover(at, lag2), _crossunder(at, lag2)
    k2 = k.barssince_nb(sell_k)
    k1 = k.barssince_nb(buy_k)
    o1 = k.barssince_nb(np.vstack([np.zeros((1, buy_k.shape[1]), bool), buy_k[:-1]]))
    o2 = k.barssince_nb(np.vstack([np.zeros((1, sell_k.shape[1]), bool), sell_k[:-1]]))
    with np.errstate(invalid="ignore"):
        return at, lag2, buy_k & (o1 > k2), sell_k & (o2 > k1), buy_k, sell_k


@indicator("OTT", ["close"], ["ott", "ott_lag2", "mavg", "direction", "buy", "sell"])
def ott(close, length=2, percent=1.4):
    """Optimized Trend Tracker [KivancOzbilgic / Anil Ozeksi] on the VAR average.

    The chart plots ``OTT[2]``; that is ``ott_lag2``, and ``buy``/``sell`` are
    mavg crossing it. VAR starts from 0, so allow a few hundred bars of warm-up.
    """
    from .filters import _var_nb

    m = _var_nb(close, int(length), 9)
    o, _, d = _ott_nb(m, float(percent))
    lag2 = shift_2d(o, 2)
    return o, lag2, m, d, _crossover(m, lag2), _crossunder(m, lag2)


@indicator("QQE", ["close"], ["rsi_ma", "trailing_line", "trend", "long_band", "short_band"])
def qqe(close, rsi_length=14, smoothing=5, factor=4.238):
    """QQE (Quantitative Qualitative Estimation), Glaz's classic script (14 / 5 / 4.238).

    QQE MOD [Mihkel00] uses this same core with 6 / 5 / 3 (and a second
    6 / 5 / 1.61 line); call ``qqe(close, 6, 5, 3.0)`` for its main line.
    """
    n = int(rsi_length)
    wilders = n * 2 - 1
    rma_ = k.ema_nb(rsi_2d(close, n), int(smoothing))
    atr_rsi = np.abs(shift_2d(rma_, 1) - rma_)
    dar = k.ema_nb(k.ema_nb(atr_rsi, wilders), wilders) * factor
    tl, tr_, lb, sb = _qqe_nb(rma_, dar)
    return rma_, tl, tr_, lb, sb


@indicator("STC", ["close"], ["stc"])
def schaff_trend_cycle(close, length=12, fast=26, slow=50, factor=0.5):
    """Schaff Trend Cycle, as in TradingView's "STC Indicator - A Better MACD [SHK]"."""
    n = int(length)
    m = k.ema_nb(close, int(fast)) - k.ema_nb(close, int(slow))
    return _stc_nb(m, k.lowest_nb(m, n), k.highest_nb(m, n), n, float(factor))


@indicator("WAE", ["high", "low", "close"], ["trend_up", "trend_down", "explosion", "dead_zone"])
def waddah_attar_explosion(high, low, close, sensitivity=150, fast=20, slow=40, channel_length=20, mult=2.0,
                           dead_zone=20.0, atr_dead_zone=False):
    """Waddah Attar Explosion [LazyBear].

    LazyBear's dead zone is the constant ``dead_zone`` input (20).
    ``atr_dead_zone=True`` uses rma(tr, 100) * 3.7 instead, as in
    "Waddah Attar Explosion V2 [SHK]".
    """
    m = k.ema_nb(close, int(fast)) - k.ema_nb(close, int(slow))
    t1 = (m - shift_2d(m, 1)) * sensitivity
    n = int(channel_length)
    e1 = 2 * mult * k.stdev_nb(close, n)
    with np.errstate(invalid="ignore"):
        up = np.where(t1 >= 0, t1, 0.0)
        dn = np.where(t1 < 0, -t1, 0.0)
    if atr_dead_zone:
        dz = np.nan_to_num(k.rma_nb(k.tr_nb(high, low, close, True), 100)) * 3.7
    else:
        dz = np.full(close.shape, float(dead_zone))
    return up, dn, e1, dz


@indicator("WVF", ["low", "close"], ["wvf", "upper_band", "range_high", "signal"])
def williams_vix_fix(low, close, period=22, bb_length=20, mult=2.0, lookback=50, percentile=0.85):
    """CM_Williams_Vix_Fix [ChrisMoody]: synthetic VIX for bottoms."""
    hc = k.highest_nb(close, int(period))
    w = safe_div(hc - low, hc) * 100
    n = int(bb_length)
    upper = k.sma_nb(w, n) + mult * k.stdev_nb(w, n)
    rh = k.highest_nb(w, int(lookback)) * percentile
    with np.errstate(invalid="ignore"):
        return w, upper, rh, (w >= upper) | (w >= rh)


@indicator("VOLATILITY_STOP", ["high", "low", "close"], ["stop", "trend"])
def volatility_stop(high, low, close, length=20, multiplier=2.0):
    """Volatility Stop (TradingView built-in, 20 / 2.0, source close)."""
    a = atr_2d(high, low, close, int(length)) * multiplier
    return _vstop_nb(close, a, k.tr_nb(high, low, close, False))


@indicator("CHANDE_KROLL_STOP", ["high", "low", "close"], ["stop_long", "stop_short"])
def chande_kroll_stop(high, low, close, p=10, x=1.0, q=9):
    """Chande Kroll Stop (TradingView built-in, 10 / 1 / 9)."""
    a = atr_2d(high, low, close, int(p))
    first_high = k.highest_nb(high, int(p)) - x * a
    first_low = k.lowest_nb(low, int(p)) + x * a
    return k.lowest_nb(first_low, int(q)), k.highest_nb(first_high, int(q))


@indicator("ATR_STOP", ["high", "low", "close"], ["long_stop", "short_stop"])
def atr_stop_loss(high, low, close, length=14, multiplier=1.5, smoothing="rma"):
    """ATR Stop Loss Finder [veryfid]: low - m*ATR / high + m*ATR."""
    a = atr_2d(high, low, close, int(length), smoothing) * multiplier
    return low - a, high + a


@indicator("STARC", ["high", "low", "close"], ["basis", "upper", "lower"])
def starc_bands(high, low, close, sma_length=6, atr_length=15, multiplier=2.0):
    """STARC Bands (Stoller): sma(close, 6) +/- 2 * ATR(15)."""
    b = k.sma_nb(close, int(sma_length))
    a = atr_2d(high, low, close, int(atr_length)) * multiplier
    return b, b + a, b - a
