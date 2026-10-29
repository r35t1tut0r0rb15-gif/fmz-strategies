"""Staging area: trend, channel and stop indicators that FMZ strategies use and
``tv_indicators`` lacks (G-Channel, TD Sequential, Renko, Pivot Point
SuperTrend, DonovanWall's Range Filter, Leledc, PMax / MOST, Recursive Bands,
Standard Error Bands, Dual Thrust, SuperIchi, ATR bands and stops...).

Like ``fmz_catalog.extra``, importing this module moves its indicators out of
the main registry into ``EXTRA_TREND``, so ``tv_indicators`` is unchanged.
Every function follows the ``tv_indicators`` conventions (pandas/numpy in,
same type out, a namedtuple for several outputs) and names its source.

Published scripts were read from TradingView's pine-facade
(``https://pine-facade.tradingview.com/pine-facade/get/<PUB id>/last``, the
text behind the chart's "Source code" button). Functions marked
*strategy-specific* port code that exists only inside one FMZ strategy.

Everything is causal: a value at bar ``t`` only uses bars ``<= t``. Pivots are
reported on the bar that confirms them, Renko reports the bricks known at
each bar's close, and nothing is shifted backwards for plotting.

    import fmz_catalog.extra_trend as xtr
    g = xtr.g_channel(df.close, 100)
    pp = xtr.pivot_point_supertrend(df.high, df.low, df.close)
"""

import math

import numpy as np
from numba import njit

from tv_indicators import kernels as k
from tv_indicators._core import REGISTRY, change_2d, indicator, ma_2d, safe_div, shift_2d
from tv_indicators.community import _range_filter_nb, _smooth_range
from tv_indicators.filters import _var_nb
from tv_indicators.oscillators import rsi_2d
from tv_indicators.volatility import atr_2d
from fmz_catalog.extra import _wwma_nb

NAN = np.nan
_BEFORE = set(REGISTRY)

_nz = k._nz
_max2 = k._max2
_min2 = k._min2


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _xover(a, b):
    """``ta.crossover(a, b)`` (na comparisons are false)."""
    with np.errstate(invalid="ignore"):
        return (a > b) & (shift_2d(a, 1) <= shift_2d(b, 1))


def _xunder(a, b):
    """``ta.crossunder(a, b)``."""
    with np.errstate(invalid="ignore"):
        return (a < b) & (shift_2d(a, 1) >= shift_2d(b, 1))


def _cross(a, b):
    """``ta.cross(a, b)``."""
    return _xover(a, b) | _xunder(a, b)


def _barssince(cond):
    return k.barssince_nb(np.ascontiguousarray(cond, dtype=np.bool_))


def _norm(s):
    return str(s).strip().lower().replace("_", " ")


@njit(cache=True)
def _pivot_nb(x, left, right, sign):
    """Private ``ta.pivothigh`` (sign=1) / ``ta.pivotlow`` (sign=-1).

    Same rule as TradingView's ZigZag library ``findPivotPoint``: the pivot is
    strictly beyond the ``left`` older bars and at least equal to the
    ``right`` newer bars. The value is reported on the confirming bar
    (``right`` bars later), so it never looks ahead. NaN in the window: none.
    """
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for i in range(left + right, x.shape[0]):
            p = x[i - right, c]
            if np.isnan(p):
                continue
            sp = sign * p
            ok = True
            for j in range(1, left + 1):
                v = x[i - right - j, c]
                if np.isnan(v) or sign * v >= sp:
                    ok = False
                    break
            if ok:
                for j in range(1, right + 1):
                    v = x[i - right + j, c]
                    if np.isnan(v) or sign * v > sp:
                        ok = False
                        break
            if ok:
                out[i, c] = p
    return out


def _kivanc_ma(src, n, ma_type, volume=None):
    """Moving averages offered by Kivanc Ozbilgic's PMax / OTT / MOST scripts
    (SMA, EMA, WMA, TMA, VAR, WWMA, ZLEMA, TSF), plus the ``ma_2d`` names and
    ``"none"`` (use ``src`` as it is, e.g. a T3 you computed yourself)."""
    n = int(n)
    kind = _norm(ma_type)
    if kind in ("none", "src", "source"):
        return src.copy()
    if kind == "tma":
        return k.sma_nb(k.sma_nb(src, int(math.ceil(n / 2))), n // 2 + 1)
    if kind in ("var", "vidya"):
        return _var_nb(src, n, 9)
    if kind == "wwma":
        return _wwma_nb(src, float(n))
    if kind == "zlema":
        return k.ema_nb(2 * src - shift_2d(src, n // 2), n)
    if kind == "tsf":
        return k.linreg_nb(src, n, -1)
    return ma_2d(src, n, kind, volume)


# ---------------------------------------------------------------------------
# G-Channel [alexgrover] and G-Channel Trend Detection [jaggedsoft]
# ---------------------------------------------------------------------------

@njit(cache=True)
def _gchannel_nb(src, n, seed_src):
    a_o = np.full(src.shape, NAN)
    b_o = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        a1 = NAN
        b1 = NAN
        for i in range(src.shape[0]):
            s = src[i, c]
            if seed_src and np.isnan(a1):
                a = s
                b = s
            else:
                d = 0.0 if (np.isnan(a1) or np.isnan(b1)) else (a1 - b1) / n
                a = _max2(s, _nz(a1)) - d
                b = _min2(s, _nz(b1)) + d
            a_o[i, c] = a
            b_o[i, c] = b
            a1 = a
            b1 = b
    return a_o, b_o


@indicator("G_CHANNEL", ["close"], ["upper", "lower", "avg", "bullish"])
def g_channel(close, length=100, seed="zero"):
    """G-Channels [alexgrover] with the trend rule of "G-Channel Trend
    Detection" [jaggedsoft], the version FMZ strategies copy.

    a = max(src, nz(a[1])) - nz(a[1]-b[1])/length,
    b = min(src, nz(b[1])) + nz(a[1]-b[1])/length, avg = (a+b)/2.
    crossup = b[1] < close[1] and b > close, crossdn = a[1] < close[1] and
    a > close, bullish = barssince(crossdn) <= barssince(crossup).

    ``seed="zero"`` is alexgrover's original (the lower band starts at 0 and
    needs a few times ``length`` bars to reach price); ``seed="source"``
    starts both bands at the first close (``na(a[1]) ? close : ...``), as
    some strategy copies do. The two converge.
    Source: PUB;ucsvQVFwNp08jVIBHddQIK44K5J1N8Un (G-Channels, alexgrover),
    PUB;YmCsEMMCosINI8dTShLrBHjl2JKqfk1B (G-Channel Trend Detection).
    """
    a, b = _gchannel_nb(close, float(length), _norm(seed) in ("source", "src", "close"))
    with np.errstate(invalid="ignore"):
        crossup = (shift_2d(b, 1) < shift_2d(close, 1)) & (b > close)
        crossdn = (shift_2d(a, 1) < shift_2d(close, 1)) & (a > close)
        bullish = _barssince(crossdn) <= _barssince(crossup)
    return a, b, (a + b) / 2, bullish


# ---------------------------------------------------------------------------
# Tom DeMark: TD Setup / TD Sequential, DeMark Reversal Points [cheatcountry]
# ---------------------------------------------------------------------------

@njit(cache=True)
def _td_nb(high, low, close, look, setup_n, cd_n, cd_look):
    shape = close.shape
    bcnt = np.zeros(shape)
    scnt = np.zeros(shape)
    bset = np.zeros(shape)
    sset = np.zeros(shape)
    bdone = np.zeros(shape, dtype=np.bool_)
    sdone = np.zeros(shape, dtype=np.bool_)
    bperf = np.zeros(shape, dtype=np.bool_)
    sperf = np.zeros(shape, dtype=np.bool_)
    bcd = np.zeros(shape)
    scd = np.zeros(shape)
    b13 = np.zeros(shape, dtype=np.bool_)
    s13 = np.zeros(shape, dtype=np.bool_)
    res_o = np.full(shape, NAN)
    sup_o = np.full(shape, NAN)
    q = cd_n - 5  # countdown bar 8 for a 13 count
    for c in range(shape[1]):
        rb = 0.0
        rs = 0.0
        sb = 0.0
        ss = 0.0
        res = NAN
        sup = NAN
        bact = False
        bc = 0
        bq = NAN
        bref_hi = NAN
        bref_tr = NAN
        sact = False
        sc = 0
        sq = NAN
        sref_lo = NAN
        sref_tr = NAN
        for i in range(shape[0]):
            cl = close[i, c]
            c4 = close[i - look, c] if i >= look else NAN
            rb = rb + 1 if cl < c4 else 0.0
            rs = rs + 1 if cl > c4 else 0.0
            p1 = close[i - 1, c] if i >= 1 else NAN
            p5 = close[i - 1 - look, c] if i >= look + 1 else NAN
            if cl < c4:
                if sb > 0:
                    sb += 1
                elif p1 > p5:  # bearish TD price flip
                    sb = 1.0
                else:
                    sb = 0.0
            else:
                sb = 0.0
            if cl > c4:
                if ss > 0:
                    ss += 1
                elif p1 < p5:  # bullish TD price flip
                    ss = 1.0
                else:
                    ss = 0.0
            else:
                ss = 0.0
            if sb == setup_n:
                bdone[i, c] = True
                if i >= 3:
                    bperf[i, c] = min(low[i, c], low[i - 1, c]) <= min(low[i - 2, c], low[i - 3, c])
                hi = -np.inf
                lo = np.inf
                for j in range(setup_n):
                    th = high[i - j, c]
                    tl = low[i - j, c]
                    if i - j - 1 >= 0:
                        pc = close[i - j - 1, c]
                        th = max(th, pc)
                        tl = min(tl, pc)
                    hi = max(hi, th)
                    lo = min(lo, tl)
                res = hi
                trn = hi - lo
                sact = False  # an opposite setup cancels the sell countdown
                sc = 0
                if (not bact) or (bref_tr <= trn < 1.618 * bref_tr):
                    bact = True  # start, or recycle onto the new setup
                    bc = 0
                    bq = NAN
                    bref_hi = hi
                    bref_tr = trn
            if ss == setup_n:
                sdone[i, c] = True
                if i >= 3:
                    sperf[i, c] = max(high[i, c], high[i - 1, c]) >= max(high[i - 2, c], high[i - 3, c])
                hi = -np.inf
                lo = np.inf
                for j in range(setup_n):
                    th = high[i - j, c]
                    tl = low[i - j, c]
                    if i - j - 1 >= 0:
                        pc = close[i - j - 1, c]
                        th = max(th, pc)
                        tl = min(tl, pc)
                    hi = max(hi, th)
                    lo = min(lo, tl)
                sup = lo
                trn = hi - lo
                bact = False
                bc = 0
                if (not sact) or (sref_tr <= trn < 1.618 * sref_tr):
                    sact = True
                    sc = 0
                    sq = NAN
                    sref_lo = lo
                    sref_tr = trn
            # true low above the buy setup's TDST (true high) cancels it
            if bact and i >= 1 and min(low[i, c], close[i - 1, c]) > bref_hi:
                bact = False
                bc = 0
            if sact and i >= 1 and max(high[i, c], close[i - 1, c]) < sref_lo:
                sact = False
                sc = 0
            if bact and i >= cd_look and cl <= low[i - cd_look, c]:
                if bc < cd_n - 1:
                    bc += 1
                    if bc == q:
                        bq = cl
                elif low[i, c] <= bq:
                    bc = cd_n
                    b13[i, c] = True
            if sact and i >= cd_look and cl >= high[i - cd_look, c]:
                if sc < cd_n - 1:
                    sc += 1
                    if sc == q:
                        sq = cl
                elif high[i, c] >= sq:
                    sc = cd_n
                    s13[i, c] = True
            bcnt[i, c] = rb
            scnt[i, c] = rs
            bset[i, c] = sb
            sset[i, c] = ss
            bcd[i, c] = bc if bact else 0.0
            scd[i, c] = sc if sact else 0.0
            res_o[i, c] = res
            sup_o[i, c] = sup
            if b13[i, c]:
                bact = False
                bc = 0
            if s13[i, c]:
                sact = False
                sc = 0
    return bcnt, scnt, bset, sset, bdone, sdone, bperf, sperf, bcd, scd, b13, s13, res_o, sup_o


@indicator("TD_SEQUENTIAL", ["high", "low", "close"],
           ["buy_count", "sell_count", "buy_setup", "sell_setup", "buy_setup_complete", "sell_setup_complete",
            "buy_perfected", "sell_perfected", "buy_countdown", "sell_countdown", "buy_13", "sell_13",
            "tdst_resistance", "tdst_support"])
def td_sequential(high, low, close, lookback=4, setup_length=9, countdown_length=13, countdown_lookback=2):
    """Tom DeMark's TD Setup and TD Sequential (rules as in Jason Perl,
    "DeMark Indicators", 2008).

    * ``buy_count`` / ``sell_count``: the plain streak ``close < close[4]``
      (``> close[4]``), uncapped. This is what the FMZ copies call TD
      (``TS := close < close[4] ? nz(TS[1]) + 1 : 0``).
    * ``buy_setup``: DeMark's TD Buy Setup count. It starts only after a
      bearish price flip (``close[1] > close[5]`` and ``close < close[4]``)
      and is complete at 9 (``buy_setup_complete``); the count keeps going
      while the streak lasts. ``buy_perfected``: low of bar 8 or 9 <= the lows
      of bars 6 and 7. ``tdst_resistance``: highest true high of the last
      completed buy setup (``tdst_support`` mirrors it for sell setups).
    * ``buy_countdown``: starts on the setup's bar 9, counts (not
      necessarily consecutive) closes <= low[2]; bar 13 also needs
      low <= close of countdown bar 8, otherwise it is deferred.
      ``buy_13`` flags the completed countdown. It is cancelled by a
      completed sell setup or by a true low above ``tdst_resistance`` of its
      setup; a new buy setup restarts it when its true range TR2 satisfies
      TR1 <= TR2 < 1.618*TR1 (recycling). Sell side mirrored.

    Not modelled: recycle rules II/III (18-bar setups), TD Combo, and
    countdown "aggressive" variants.
    """
    return _td_nb(high, low, close, int(lookback), float(setup_length), int(countdown_length),
                  int(countdown_lookback))


@indicator("DEMARK_REVERSAL_POINTS", ["close"], ["drp", "signal", "up_count", "down_count"])
def demark_reversal_points(close, length=9, lb_length=4):
    """Demark Reversal Points [CC] (Franklin Moormann / cheatcountry).

    Counts, over the last ``length`` bars, closes above / below the close
    ``lb_length`` bars earlier (``nz`` treats missing history as 0, as the
    script does). drp = 1 when all ``length`` are down (buy), -1 when all are
    up. ``signal``: 1 if drp > 0 or ups > downs, -1 if drp < 0 or downs > ups.
    The script trades ``crossover(drp, 0)`` / ``crossunder(drp, 0)``.
    "Demark Setup Indicator [CC]" is the same with ``length = lb_length = 4``.
    """
    n, lb = int(length), int(lb_length)
    up = np.zeros(close.shape)
    dn = np.zeros(close.shape)
    for i in range(n):
        a = np.nan_to_num(shift_2d(close, i))
        b = np.nan_to_num(shift_2d(close, i + lb))
        up += a > b
        dn += a < b
    drp = np.where(dn == n, 1.0, np.where(up == n, -1.0, 0.0))
    sig = np.where((drp > 0) | (up > dn), 1.0, np.where((drp < 0) | (dn > up), -1.0, 0.0))
    return drp, sig, up, dn


# ---------------------------------------------------------------------------
# Renko (non-repainting) and Sizeblock
# ---------------------------------------------------------------------------

@njit(cache=True)
def _renko_nb(close, size, pct):
    shape = close.shape
    bo = np.full(shape, NAN)
    bc = np.full(shape, NAN)
    dr = np.zeros(shape)
    nb_o = np.zeros(shape)
    for c in range(shape[1]):
        ref = NAN  # first close: the grid starts here
        lo_ = NAN
        lc = NAN
        d = 0.0
        for i in range(shape[0]):
            x = close[i, c]
            nb = 0
            if not np.isnan(x):
                if np.isnan(ref):
                    ref = x
                    lc = x
                else:
                    for _ in range(100000):
                        s = lc * pct / 100.0 if pct > 0 else size[i, c]
                        if np.isnan(s) or s <= 0:
                            break
                        if d >= 0 and x >= lc + s:
                            lo_ = lc
                            lc = lc + s
                            d = 1.0
                            nb += 1
                        elif d <= 0 and x <= lc - s:
                            lo_ = lc
                            lc = lc - s
                            d = -1.0
                            nb -= 1
                        elif d == 1.0 and x <= lo_ - s:
                            lc = lo_ - s  # reversal: new brick from the last brick's open
                            d = -1.0
                            nb -= 1
                        elif d == -1.0 and x >= lo_ + s:
                            lc = lo_ + s
                            d = 1.0
                            nb += 1
                        else:
                            break
            if d != 0:
                bo[i, c] = lo_
                bc[i, c] = lc
            dr[i, c] = d
            nb_o[i, c] = nb
    return bo, bc, dr, nb_o


@indicator("RENKO", ["high", "low", "close"], ["brick_open", "brick_close", "direction", "new_bricks"])
def renko(high, low, close, method="atr", box_size=1.0, atr_length=14, percent=1.0):
    """Renko bricks built from closes, as known at each bar's close.

    TradingView's Renko rules: a brick in the trend direction needs a close
    one box beyond the last brick's close; a reversal needs a close one box
    beyond the last brick's open (two boxes from its close). One bar can form
    several bricks (``new_bricks`` is their signed count). The grid starts at
    the first close; ``brick_open`` / ``brick_close`` are NaN until the first
    brick and ``direction`` is +1 / -1 (0 before the first brick).

    ``method``: "traditional" (fixed ``box_size``), "atr" (box = ATR(atr_length)
    of the bar being processed) or "percentage" (box = ``percent`` % of the
    last brick close). TradingView's own ATR box uses the ATR of the last
    chart bar for the whole history, which is look-ahead; here the box only
    uses data up to the current bar, so nothing repaints.
    """
    m = _norm(method)
    if m == "atr":
        size = atr_2d(high, low, close, int(atr_length))
        pct = 0.0
    elif m in ("traditional", "fixed", "box"):
        size = np.full(close.shape, float(box_size))
        pct = 0.0
    elif m in ("percentage", "percent", "%"):
        size = np.full(close.shape, NAN)
        pct = float(percent)
    else:
        raise ValueError("method must be 'atr', 'traditional' or 'percentage'")
    return _renko_nb(close, size, pct)


@njit(cache=True)
def _rnd(x, tick):
    return math.floor(x / tick + 0.5) * tick if tick > 0 else x


@njit(cache=True)
def _sizeblock_nb(open_, high, low, close, v, vb, ticks, use_hl, tick):
    shape = close.shape
    xo = np.full(shape, NAN)
    ho = np.full(shape, NAN)
    lo = np.full(shape, NAN)
    for c in range(shape[1]):
        xp = NAN
        hp = NAN
        lp = NAN
        for i in range(shape[0]):
            a = open_[i, c]
            b = close[i, c]
            cc = _rnd(high[i, c], tick) if use_hl else _rnd(b, tick)
            dd = _rnd(low[i, c], tick) if use_hl else _rnd(b, tick)
            x = _rnd(a, tick) if np.isnan(xp) else xp
            if ticks:
                h = _rnd(x + v, tick)
                l = _rnd(x - v, tick)
            else:
                h = _rnd(x * (1 + v / 100), tick)
                l = _rnd(x * (1 - v / 100), tick)
            if not np.isnan(hp):
                h = hp
            if not np.isnan(lp):
                l = lp
            if v > 0:
                if cc >= h and b > a:
                    while cc >= h:
                        x = h
                        hn = _rnd(h + v, tick) if ticks else _rnd(h * (1 + v / 100), tick)
                        l = _rnd(x - vb, tick) if ticks else _rnd(x * (1 - vb / 100), tick)
                        if not hn > h:
                            break
                        h = hn
                if dd <= l and b < a:
                    while dd <= l:
                        x = l
                        ln = _rnd(l - v, tick) if ticks else _rnd(l * (1 - v / 100), tick)
                        h = _rnd(x + vb, tick) if ticks else _rnd(x * (1 + vb / 100), tick)
                        if not ln < l:
                            break
                        l = ln
            xo[i, c] = x
            ho[i, c] = h
            lo[i, c] = l
            xp = x
            hp = h
            lp = l
    return xo, ho, lo


@indicator("SIZEBLOCK", ["open", "high", "low", "close"], ["mid", "upper", "lower"])
def sizeblock(open, high, low, close, deviation=1.0, u_turn=2.0, dev_type="percentage", source="close",
              mintick=0.0):
    """Sizeblock (strategy-specific, FMZ "趋势成块策略Sizeblock-Strategy",
    function ``Assembling``): a Renko-like row of fixed-size blocks.

    The row moves up by whole ``deviation`` steps (percent or ticks) on a
    bullish bar whose close (or high, ``source="highlow"``) reaches the upper
    limit, and the opposite limit is then set ``u_turn`` away; down moves
    mirror it. ``mintick`` > 0 reproduces ``math.round_to_mintick``.
    """
    ticks = _norm(dev_type) == "ticks"
    v = float(deviation) * (mintick if ticks else 1.0)
    vb = float(u_turn) * (mintick if ticks else 1.0)
    return _sizeblock_nb(open, high, low, close, v, vb, ticks, _norm(source) == "highlow", float(mintick))


# ---------------------------------------------------------------------------
# Pivot Point SuperTrend [LonesomeTheBlue]
# ---------------------------------------------------------------------------

@njit(cache=True)
def _ppst_nb(ph, pl, atr, close, factor):
    shape = close.shape
    tr_o = np.full(shape, NAN)
    tdir = np.full(shape, NAN)
    cen_o = np.full(shape, NAN)
    tup_o = np.full(shape, NAN)
    tdn_o = np.full(shape, NAN)
    sup_o = np.full(shape, NAN)
    res_o = np.full(shape, NAN)
    for c in range(shape[1]):
        center = NAN
        tup1 = NAN
        tdn1 = NAN
        trend1 = NAN
        sup = NAN
        res = NAN
        for i in range(shape[0]):
            h = ph[i, c]
            l_ = pl[i, c]
            lastpp = h if not np.isnan(h) else l_
            if not np.isnan(lastpp) and lastpp != 0:  # Pine v4 `if lastpp`
                center = lastpp if np.isnan(center) else (center * 2 + lastpp) / 3
            up = center - factor * atr[i, c]
            dn = center + factor * atr[i, c]
            pc = close[i - 1, c] if i > 0 else NAN
            tup = _max2(up, tup1) if pc > tup1 else up
            tdn = _min2(dn, tdn1) if pc < tdn1 else dn
            cl = close[i, c]
            if cl > tdn1:
                trend = 1.0
            elif cl < tup1:
                trend = -1.0
            else:
                trend = 1.0 if np.isnan(trend1) else trend1
            if not np.isnan(l_) and l_ != 0:
                sup = l_
            if not np.isnan(h) and h != 0:
                res = h
            tr_o[i, c] = tup if trend == 1.0 else tdn
            tdir[i, c] = trend
            cen_o[i, c] = center
            tup_o[i, c] = tup
            tdn_o[i, c] = tdn
            sup_o[i, c] = sup
            res_o[i, c] = res
            tup1 = tup
            tdn1 = tdn
            trend1 = trend
    return tr_o, tdir, cen_o, tup_o, tdn_o, sup_o, res_o


@indicator("PIVOT_POINT_SUPERTREND", ["high", "low", "close"],
           ["supertrend", "trend", "center", "up", "down", "support", "resistance", "buy", "sell"])
def pivot_point_supertrend(high, low, close, period=2, factor=3.0, atr_period=10):
    """Pivot Point SuperTrend [LonesomeTheBlue] (PUB;HN4w1eNW3B9HP5oSa2MNMIHMYUqLPHUT).

    Center = (2*center + new pivot) / 3 on each confirmed pivot high / low
    (``ta.pivothigh(period, period)``, high first); bands center -+
    factor*ATR(atr_period) trail like a SuperTrend. ``trend`` is 1 / -1, the
    script's own convention. Pivots, center and support / resistance are
    known ``period`` bars after the pivot bar (the script only *draws* them
    ``period`` bars back). Uses a private copy of ``ta.pivothigh`` /
    ``ta.pivotlow`` (strictly above the left bars, >= the right bars).
    """
    p = int(period)
    ph = _pivot_nb(high, p, p, 1.0)
    pl = _pivot_nb(low, p, p, -1.0)
    st, tr, cen, up, dn, sup, res = _ppst_nb(ph, pl, atr_2d(high, low, close, int(atr_period)), close, float(factor))
    t1 = shift_2d(tr, 1)
    return st, tr, cen, up, dn, sup, res, (tr == 1) & (t1 == -1), (tr == -1) & (t1 == 1)


# ---------------------------------------------------------------------------
# Range Filter [DW] (DonovanWall)
# ---------------------------------------------------------------------------

@njit(cache=True)
def _cond_ema_nb(x, cond, n):
    """DonovanWall's ``Cond_EMA``: an EMA sampled only when ``cond`` is true,
    seeded with the first sample (a NaN sample makes it NaN until reseeded)."""
    out = np.full(x.shape, NAN)
    alpha = 2.0 / (n + 1.0)
    for c in range(x.shape[1]):
        e = NAN
        for i in range(x.shape[0]):
            if cond[i, c]:
                v = x[i, c]
                if np.isnan(e):
                    e = v
                e = (v - e) * alpha + e
            out[i, c] = e
    return out


@njit(cache=True)
def _cond_sma_all_nb(x, n):
    """``Cond_SMA(x, 1, n)``: mean of the last min(bars, n) values."""
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for i in range(x.shape[0]):
            m = min(i + 1, n)
            s = 0.0
            for j in range(m):
                s += x[i - j, c]
            out[i, c] = s / m
    return out


@njit(cache=True)
def _rf_dw_nb(h, l, r, type2):
    out = np.full(h.shape, NAN)
    for c in range(h.shape[1]):
        f = (h[0, c] + l[0, c]) / 2
        for i in range(h.shape[0]):
            prev = f
            rr = r[i, c]
            if not type2:
                if h[i, c] - rr > prev:
                    f = h[i, c] - rr
                if l[i, c] + rr < prev:
                    f = l[i, c] + rr
            else:
                if h[i, c] >= prev + rr:
                    f = prev + math.floor(abs(h[i, c] - prev) / rr) * rr if rr != 0 else NAN  # Pine: x/0 is na
                if l[i, c] <= prev - rr:
                    f = prev - math.floor(abs(l[i, c] - prev) / rr) * rr if rr != 0 else NAN
            out[i, c] = f
    return out


@njit(cache=True)
def _fdir_nb(f):
    out = np.zeros(f.shape)
    for c in range(f.shape[1]):
        d = 0.0
        for i in range(1, f.shape[0]):
            if f[i, c] > f[i - 1, c]:
                d = 1.0
            elif f[i, c] < f[i - 1, c]:
                d = -1.0
            out[i, c] = d
    return out


@indicator("RANGE_FILTER_DW", ["high", "low", "close"], ["filter", "high_band", "low_band", "direction"])
def range_filter_dw(high, low, close, filter_type=1, movement_source="close", range_size=2.618,
                    range_scale="average change", range_period=14, smooth_range=True, smooth_period=27,
                    average_filter=False, average_samples=2, mintick=0.01, pointvalue=1.0):
    """Range Filter [DW] (DonovanWall, v4 array version,
    PUB;pshyCmQSqlUKsVQ4FrNUAuGkurQPg3ty). Defaults are the script's.

    ``filter_type`` 1 (original: follow h - r / l + r) or 2 (move in whole
    multiples of r). ``movement_source`` "close" or "wicks". ``range_scale``:
    "average change" (EMA of |change(hl2 of the source)|), "atr"
    (conditional EMA of ``ta.tr(true)``, not RMA), "standard deviation",
    "% of price", "points" (x ``pointvalue``), "pips" (x 0.0001), "ticks"
    (x ``mintick``) or "absolute". Every EMA here is the script's
    ``Cond_EMA`` (seeded with the first value). ``average_filter`` averages
    filter / bands with an EMA sampled only when the filter changes.
    ``direction``: 1 rising, -1 falling (0 before the first move).
    """
    wicks = _norm(movement_source) == "wicks"
    hv = high if wicks else close
    lv = low if wicks else close
    x = (hv + lv) / 2
    n = int(range_period)
    ones = np.ones(close.shape, dtype=np.bool_)
    scale = _norm(range_scale)
    q = float(range_size)
    if scale == "average change":
        rng = q * _cond_ema_nb(np.abs(change_2d(x)), ones, n)
    elif scale == "atr":
        rng = q * _cond_ema_nb(k.tr_nb(high, low, close, True), ones, n)
    elif scale == "standard deviation":
        with np.errstate(invalid="ignore"):
            rng = q * np.sqrt(_cond_sma_all_nb(x * x, n) - _cond_sma_all_nb(x, n) ** 2)
    elif scale == "% of price":
        rng = close * q / 100
    elif scale == "points":
        rng = np.full(close.shape, q * pointvalue)
    elif scale == "pips":
        rng = np.full(close.shape, q * 0.0001)
    elif scale == "ticks":
        rng = np.full(close.shape, q * mintick)
    elif scale == "absolute":
        rng = np.full(close.shape, q)
    else:
        raise ValueError(f"unknown range_scale {range_scale!r}")
    r = _cond_ema_nb(rng, ones, int(smooth_period)) if smooth_range else rng
    f = _rf_dw_nb(np.ascontiguousarray(hv), np.ascontiguousarray(lv), r, int(filter_type) == 2)
    hb, lb = f + r, f - r
    if average_filter:
        with np.errstate(invalid="ignore"):
            chg = f != shift_2d(f, 1)
        chg[0] = False  # rng_filt1[1] is na on the first bar
        m = int(average_samples)
        f, hb, lb = _cond_ema_nb(f, chg, m), _cond_ema_nb(hb, chg, m), _cond_ema_nb(lb, chg, m)
    return f, hb, lb, _fdir_nb(f)


# ---------------------------------------------------------------------------
# Leledc Exhaustion [glaz / Joy_Bangla]
# ---------------------------------------------------------------------------

@njit(cache=True)
def _lele_nb(open_, high, low, close, hh, ll, qual, look, k_back):
    shape = close.shape
    out = np.zeros(shape)
    for c in range(shape[1]):
        bh = np.zeros(shape[0])
        sh = np.zeros(shape[0])
        for i in range(shape[0]):
            b = bh[i - k_back] if i >= k_back else 0.0
            s = sh[i - k_back] if i >= k_back else 0.0
            ret = 0.0
            cl = close[i, c]
            cp = close[i - look, c] if i >= look else NAN
            if cl > cp:
                b += 1
            if cl < cp:
                s += 1
            if b > qual and cl < open_[i, c] and high[i, c] >= hh[i, c]:
                b = 0.0
                ret = -1.0
            if s > qual and cl > open_[i, c] and low[i, c] <= ll[i, c]:
                s = 0.0
                ret = 1.0
            bh[i] = b
            sh[i] = s
            out[i, c] = ret
    return out


@indicator("LELEDC_EXHAUSTION", ["open", "high", "low", "close"], ["major", "minor"])
def leledc_exhaustion(open, high, low, close, major_qual=6, major_len=30, minor_qual=5, minor_len=5,
                      close_lookback=4, index_lookback=1):
    """Leledc Exhaustion Bar (glaz's Pine v2 original, as ported by Joy_Bangla,
    PUB;rhuzP1VuglKPh1DqvHKEoJO2a9LdLKIy).

    Counts closes above / below the close ``close_lookback`` bars back (the
    counts are *not* reset by an opposite close). A bearish bar making the
    ``len``-bar high after more than ``qual`` up counts is an exhaustion top
    (-1, count reset); a bullish bar at the ``len``-bar low after more than
    ``qual`` down counts is a bottom (+1). ``major`` = (6, 30), ``minor`` =
    (5, 5). ``index_lookback`` is Joy_Bangla's "bindexSindex" (1 = the
    original ``nz(bindex[1])``).
    """
    out = []
    for q, n in ((major_qual, major_len), (minor_qual, minor_len)):
        n = int(n)
        out.append(_lele_nb(open, high, low, close, k.highest_nb(high, n), k.lowest_nb(low, n), float(q),
                            int(close_lookback), int(index_lookback)))
    return tuple(out)


# ---------------------------------------------------------------------------
# QuantNomad's significant (ATR-margin) pivots
# ---------------------------------------------------------------------------

@njit(cache=True)
def _pivot_atr_nb(x, atr, left, right, sign):
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for i in range(left + right, x.shape[0]):
            p = x[i - right, c]
            a = atr[i, c]
            if np.isnan(p) or np.isnan(a):
                continue
            ok = True
            for j in range(1, left + 1):
                v = x[i - right - j, c]
                if np.isnan(v) or sign * p < sign * v + a:
                    ok = False
                    break
            if ok:
                for j in range(right):
                    v = x[i - j, c]
                    if np.isnan(v) or sign * p < sign * v + a:
                        ok = False
                        break
            if ok:
                out[i, c] = p
    return out


@indicator("PIVOT_ATR", ["high", "low", "close"], ["pivot_high", "pivot_low"])
def pivot_atr(high, low, close, left=4, right=2, atr_length=14, atr_mult=0.1):
    """Significant pivots of "Pivot of Pivot Reversal Strategy [QuantNomad]"
    (``pivotHighSig`` / ``pivotLowSig``), strategy-specific.

    high[right] must be at least ATR*atr_mult above each of the ``left``
    older and ``right`` newer highs (lows mirrored), using the ATR of the
    confirming bar. Reported on the confirming bar. Unlike the script, a
    window with missing data (or a NaN ATR) gives no pivot: the script's
    ``na`` comparisons are false, so it flags every bar of the warm-up.
    """
    a = atr_2d(high, low, close, int(atr_length)) * float(atr_mult)
    return (_pivot_atr_nb(high, a, int(left), int(right), 1.0),
            _pivot_atr_nb(low, a, int(left), int(right), -1.0))


# ---------------------------------------------------------------------------
# Rolling OLS of y on x
# ---------------------------------------------------------------------------

@njit(cache=True)
def _ols_nb(y, x, n):
    a_o = np.full(y.shape, NAN)
    b_o = np.full(y.shape, NAN)
    for c in range(y.shape[1]):
        for i in range(n - 1, y.shape[0]):
            mx = 0.0
            my = 0.0
            for j in range(n):
                mx += x[i - j, c]
                my += y[i - j, c]
            mx /= n
            my /= n
            sxy = 0.0
            sxx = 0.0
            for j in range(n):
                dx = x[i - j, c] - mx
                sxy += dx * (y[i - j, c] - my)
                sxx += dx * dx
            if sxx > 0:
                b = sxy / sxx
                b_o[i, c] = b
                a_o[i, c] = my - b * mx
    return a_o, b_o


@indicator("OLS_REGRESSION", ["y", "x"], ["intercept", "slope"])
def ols_regression(y, x, length=21):
    """Rolling least squares y = a + b*x over ``length`` bars (both
    deviations from the *window's* means). NaN if x is constant.

    The FMZ ``linregs(y, x, len)`` copies compute
    ``sum((x - xbar)*(y - ybar), len) / sum((x - xbar)^2, len)`` with ``xbar``
    and ``ybar`` as series, so each bar uses its own rolling mean: that is
    not the OLS slope. This function gives the real one.
    """
    return _ols_nb(y, x, int(length))


# ---------------------------------------------------------------------------
# MOST [Anil Ozeksi / KivancOzbilgic] and PMax [KivancOzbilgic]
# ---------------------------------------------------------------------------

@njit(cache=True)
def _stop_dir_nb(m, dist):
    """Kivanc's long/short stop pair with a direction flip (MOST, PMax, OTT)."""
    shape = m.shape
    out = np.full(shape, NAN)
    dir_o = np.full(shape, NAN)
    for c in range(shape[1]):
        ls1 = NAN
        ss1 = NAN
        d = 1.0
        for i in range(shape[0]):
            mm = m[i, c]
            ls = mm - dist[i, c]
            lsp = ls if np.isnan(ls1) else ls1
            if mm > lsp:
                ls = _max2(ls, lsp)
            ss = mm + dist[i, c]
            ssp = ss if np.isnan(ss1) else ss1
            if mm < ssp:
                ss = _min2(ss, ssp)
            if d == -1.0 and mm > ssp:
                d = 1.0
            elif d == 1.0 and mm < lsp:
                d = -1.0
            out[i, c] = ls if d == 1.0 else ss
            dir_o[i, c] = d
            ls1 = ls
            ss1 = ss
    return out, dir_o


@njit(cache=True)
def _side_nb(a, b):
    out = np.full(a.shape, NAN)
    for c in range(a.shape[1]):
        d = NAN
        for i in range(a.shape[0]):
            if a[i, c] > b[i, c]:
                d = 1.0
            elif a[i, c] < b[i, c]:
                d = -1.0
            out[i, c] = d
    return out


@indicator("MOST", ["close"], ["most", "mavg", "direction"])
def most(close, length=3, percent=2.0, ma_type="ema", method="kivanc"):
    """MOST, Moving Stop Loss (Anil Ozeksi; KivancOzbilgic's TradingView code).

    ``method="kivanc"``: the long/short stop pair of Kivanc's MOST / OTT code
    (exMov -+ exMov*percent/100, each ratcheting, and a direction flip),
    the same line as ``OTT``'s MOST line (``mt``).
    ``method="trailing"``: the older single-line form some copies use
    (``mostfiyat`` in "Moving Average Tracking Stop Loss", ``Trail2`` in
    "Y-Profit Maximizer"): UT Bot's recursion on the average with a stop of
    average*percent/100.
    ``ma_type``: sma, ema, wma, tma, var, wwma, zlema, tsf or any ``ma_2d``
    name; "none" uses ``close`` as the average (pass your own T3/HullEMA).
    ``direction`` is 1 / -1 (for "trailing": side of the average vs MOST).
    """
    m = _kivanc_ma(close, length, ma_type)
    dist = m * float(percent) / 100
    if _norm(method) == "trailing":
        line, _ = k.utbot_nb(m, dist)
        return line, m, _side_nb(m, line)
    line, d = _stop_dir_nb(m, dist)
    return line, m, d


@indicator("PMAX", ["high", "low", "close"], ["pmax", "mavg", "direction", "buy", "sell"])
def pmax(high, low, close, atr_length=10, multiplier=3.0, ma_type="ema", ma_length=10, change_atr=True,
         normalize=False, source="hl2"):
    """Profit Maximizer (PMax) [KivancOzbilgic] (PUB;ps6kWkOWqLJPZhvTAj2ORDYjN1ewE9gA).

    MOST's stop pair with an ATR distance: MAvg -+ multiplier*ATR (divided by
    close when ``normalize``). ``change_atr=True`` uses ``ta.atr`` (RMA),
    False the script's ``sma(tr)``. ``source``: hl2 (default), close, hlc3,
    high or low. ``buy`` / ``sell``: MAvg crossing PMax. For other inputs
    (a T3 of RSI, an RSI-based ATR...) use ``pmax_core``.
    """
    s = _norm(source)
    src = {"hl2": (high + low) / 2, "hlc3": (high + low + close) / 3, "close": close, "high": high,
           "low": low}.get(s)
    if src is None:
        raise ValueError("source must be hl2, hlc3, close, high or low")
    n = int(atr_length)
    atr = atr_2d(high, low, close, n) if change_atr else k.sma_nb(k.tr_nb(high, low, close, False), n)
    m = _kivanc_ma(src, ma_length, ma_type)
    dist = float(multiplier) * (safe_div(atr, close) if normalize else atr)
    line, d = _stop_dir_nb(m, dist)
    return line, m, d, _xover(m, line), _xunder(m, line)


@indicator("PMAX_CORE", ["mavg", "atr"], ["pmax", "direction"])
def pmax_core(mavg, atr, multiplier=3.0):
    """PMax line from a precomputed average and ATR (``Pmax_Func`` of the FMZ
    "PMax + RSI + T3" strategy: PMax of a T3 of RSI with an RSI true range)."""
    return _stop_dir_nb(mavg, atr * float(multiplier))


# ---------------------------------------------------------------------------
# ATR stops and bands written inside FMZ strategies
# ---------------------------------------------------------------------------

@njit(cache=True)
def _atr_support_nb(low, atr, src):
    out = np.full(low.shape, NAN)
    for c in range(low.shape[1]):
        t1 = NAN
        for i in range(low.shape[0]):
            al = low[i, c] - atr[i, c]
            if np.isnan(t1):
                t = al
            else:
                t = al if al >= t1 else t1
            if src[i, c] <= t:
                t = al
            out[i, c] = t
            t1 = t
    return out


@indicator("ATR_TRAILING_SUPPORT", ["high", "low", "close"], ["support"])
def atr_trailing_support(high, low, close, length=14):
    """Ratcheting ATR support (strategy-specific, ``ATR_func`` of the FMZ
    "Bidirectional / Dual Moving Average Reversion" strategies).

    low - ATR, raised whenever a higher value appears, and reset to the
    current low - ATR once close touches it.
    """
    return _atr_support_nb(low, atr_2d(high, low, close, int(length)), close)


@njit(cache=True)
def _river_bands_nb(high, low, close, nloss, uw, lw):
    shape = close.shape
    up_o = np.full(shape, NAN)
    lo_o = np.full(shape, NAN)
    ts_o = np.full(shape, NAN)
    pos_o = np.zeros(shape)
    for c in range(shape[1]):
        u1 = NAN
        l1 = NAN
        t1 = NAN
        pos = 0.0
        for i in range(shape[0]):
            h = high[i, c]
            lo = low[i, c]
            h1 = high[i - 1, c] if i > 0 else NAN
            lo1 = low[i - 1, c] if i > 0 else NAN
            c1 = close[i - 1, c] if i > 0 else NAN
            nl = nloss[i, c]
            pu = _nz(u1)
            hu = h + nl + uw[i, c]
            u = _min2(pu, hu) if (h < pu and h1 < pu) else hu
            pl = _nz(l1)
            ll_ = lo - nl - lw[i, c]
            l = _max2(pl, ll_) if (lo > pl and lo1 > pl) else ll_
            pt = _nz(t1)
            if lo > pt and lo1 > pt:
                t = _max2(pt, ll_)
            elif h < pt and h1 < pt:
                t = _min2(pt, hu)
            elif lo <= pt and c1 > pt:
                t = u1
            elif h >= pt and c1 < pt:
                t = l1
            else:
                t = 0.0
            if c1 > pt and lo <= pt:
                pos = 1.0
            elif c1 < pt and h >= pt:
                pos = -1.0
            up_o[i, c] = u
            lo_o[i, c] = l
            ts_o[i, c] = t
            pos_o[i, c] = pos
            u1 = u
            l1 = l
            t1 = t
    return up_o, lo_o, ts_o, pos_o


@indicator("ATR_TRAILING_BANDS", ["open", "high", "low", "close"], ["upper", "lower", "stop", "pos"])
def atr_trailing_bands(open, high, low, close, atr_length=5, mult=4.0, wick_length=30, wick_type="avg"):
    """"ATR Trailing Stop Bands Strategy [R]" (River's mod of HPotter's port
    of Sylvain Vervoort's ATR trailing stop, TASC June 2009), strategy-specific.

    Bands high + mult*ATR + upper wick and low - mult*ATR - lower wick
    ratchet while price stays inside; the trailing stop jumps to the
    previous opposite band when crossed (0 when none of the cases holds,
    as in the script). Wick protection: SMA (``wick_type="avg"``) or highest
    (``"max"``) of the previous bar's wick over ``wick_length`` bars.
    ``pos``: 1 after a down-cross of the stop, -1 after an up-cross (the
    script colours 1 red and -1 green).
    """
    n = int(wick_length)
    o1, h1, l1, c1 = (shift_2d(x, 1) for x in (open, high, low, close))
    with np.errstate(invalid="ignore"):
        uwick = np.where(c1 <= o1, h1 - o1, h1 - c1)
        lwick = np.where(c1 > o1, o1 - l1, c1 - l1)
    if _norm(wick_type) == "max":
        uw, lw = k.highest_nb(uwick, n), k.highest_nb(lwick, n)
    else:
        uw, lw = k.sma_nb(uwick, n), k.sma_nb(lwick, n)
    nloss = float(mult) * atr_2d(high, low, close, int(atr_length))
    return _river_bands_nb(high, low, close, nloss, uw, lw)


@njit(cache=True)
def _claw_nb(high, low, close, atrm):
    shape = close.shape
    up_o = np.full(shape, NAN)
    lo_o = np.full(shape, NAN)
    for c in range(shape[1]):
        u1 = NAN
        l1 = NAN
        for i in range(shape[0]):
            u = high[i, c] + atrm[i, c]
            l = low[i, c] - atrm[i, c]
            if u > u1 and close[i, c] < u1:
                u = u1
            if l < l1 and close[i, c] > l1:
                l = l1
            up_o[i, c] = u
            lo_o[i, c] = l
            u1 = u
            l1 = l
    return up_o, lo_o


@indicator("ATR_BREAKOUT_BANDS", ["high", "low", "close"], ["upper", "lower", "state"])
def atr_breakout_bands(high, low, close, atr_length=120, mult=2.0):
    """ATR trend bands of the FMZ "Claw-Pattern" / ATR Trend Breakout
    strategy (Trading Strategy Guides), strategy-specific.

    upper = high + mult*ATR, held at its previous value while it would rise
    and close is below it; lower = low - mult*ATR, held while it would fall
    and close is above it. ``state`` = -1 when close last crossed the
    previous lower band more recently than the previous upper band (the
    script shows the upper band), else 1.
    """
    u, l = _claw_nb(high, low, close, float(mult) * atr_2d(high, low, close, int(atr_length)))
    with np.errstate(invalid="ignore"):
        st = np.where(_barssince(_cross(close, shift_2d(u, 1))) > _barssince(_cross(close, shift_2d(l, 1))),
                      -1.0, 1.0)
    return u, l, st


@njit(cache=True)
def _wilder_trail_nb(close, upper, lower):
    out = np.full(close.shape, NAN)
    for c in range(close.shape[1]):
        t1 = NAN
        for i in range(close.shape[0]):
            u1 = upper[i - 1, c] if i > 0 else NAN
            l1 = lower[i - 1, c] if i > 0 else NAN
            cl = close[i, c]
            if np.isnan(t1):
                t = l1
            elif cl < t1:
                t = u1
            elif cl > t1:
                t = l1
            else:
                t = t1
            out[i, c] = t
            t1 = t
    return out


@indicator("WILDER_VOLATILITY_TRAIL", ["high", "low", "close"], ["stop", "upper_trail", "lower_trail"])
def wilder_volatility_trail(high, low, close, atr_mult=3.0, atr_length=7, atr_ma="rma", sic_type="close"):
    """"Wilder's Volatility Trailing Stop Strategy with various MA's"
    [SparkyFlary], strategy-specific (FMZ "Adaptive Trend Tracking Stop Loss").

    upper = lowest(close, n) + mult*ATR, lower = highest(close, n) - mult*ATR
    (``sic_type="high-low"`` uses low / high); the stop switches to the
    previous bar's upper trail when close is below it and to the previous
    lower trail when close is above it. ``atr_ma``: rma, ema, sma or hma.
    Wilder's own Volatility System uses the extreme close since entry
    instead of a rolling window.

    Fix: the script declares ``float TS = 0`` (not ``var``), so on a bar
    whose close equals the previous stop the stop drops to 0; here it holds.
    """
    n = int(atr_length)
    kind = _norm(atr_ma)
    atr = ma_2d(k.tr_nb(high, low, close, False), n, "hma" if kind == "hull" else kind)
    hl = _norm(sic_type) == "high-low"
    upper = k.lowest_nb(low if hl else close, n) + float(atr_mult) * atr
    lower = k.highest_nb(high if hl else close, n) - float(atr_mult) * atr
    return _wilder_trail_nb(close, upper, lower), upper, lower


@njit(cache=True)
def _trend_trader_nb(close, hi, lo):
    shape = close.shape
    ret_o = np.full(shape, NAN)
    pos_o = np.full(shape, NAN)
    for c in range(shape[1]):
        r = 0.0
        p = 0.0
        for i in range(shape[0]):
            x = close[i, c]
            if x > hi[i, c] and x > lo[i, c]:
                r = hi[i, c]
            elif x < lo[i, c] and x < hi[i, c]:
                r = lo[i, c]
            if x > r:
                p = 1.0
            elif x < r:
                p = -1.0
            ret_o[i, c] = r
            pos_o[i, c] = p
    return ret_o, pos_o


@indicator("TREND_TRADER", ["high", "low", "close"], ["trend_line", "pos"])
def trend_trader(high, low, close, length=21, multiplier=3.0):
    """Andrew Abraham's Trend Trader ("Trading the Trend", TASC Sept 1998),
    as coded in HPotter's "Trend Trader Strategy" and in the FMZ
    "OCC Trend Combo" (``ret`` / ``pos``).

    avgTR = wma(TR, length); hiLimit = highest(high)[1] - avgTR[1]*mult,
    loLimit = lowest(low)[1] + avgTR[1]*mult. The line takes hiLimit when
    close is above both limits, loLimit when below both, else holds (0 at
    the start, like the script's ``nz(ret[1], 0)``). ``pos`` = side of close.
    Pine v4 ``highest(length)`` / ``lowest(length)`` use high / low.
    """
    n = int(length)
    avg = k.wma_nb(k.tr_nb(high, low, close, False), n)
    hi = shift_2d(k.highest_nb(high, n) - avg * float(multiplier), 1)
    lo = shift_2d(k.lowest_nb(low, n) + avg * float(multiplier), 1)
    return _trend_trader_nb(close, hi, lo)


@njit(cache=True)
def _flip_nb(high, low, close, lo_off, so_off):
    out = np.full(close.shape, NAN)
    for c in range(close.shape[1]):
        t1 = NAN
        t2 = NAN
        for i in range(close.shape[0]):
            lo = low[i, c]
            hi = high[i, c]
            p = close[i, c]
            lo1 = low[i - 1, c] if i > 0 else NAN
            hi1 = high[i - 1, c] if i > 0 else NAN
            if lo <= t1 and lo1 >= t2:
                t = p + so_off
            elif hi >= t1 and hi1 <= t2:
                t = p - lo_off
            elif hi > t1:
                t = max(hi - lo_off, t1)
            elif lo < t1:
                t = min(lo + so_off, t1)
            else:
                t = p
            out[i, c] = t
            t2 = t1
            t1 = t
    return out


@indicator("TRAILING_STOP_FLIP", ["high", "low", "close"], ["stop"])
def trailing_stop_flip(high, low, close, long_offset=228.5, short_offset=243.5):
    """"BitMex Trailing Stop Strategy" by River (FMZ "Dynamic Trailing Stop"),
    strategy-specific: a price-offset trailing line that follows new highs
    (high - long_offset) or lows (low + short_offset) and flips when price
    pierces it. Below the line = short side. The script feeds 1-minute data
    through ``security``; pass whatever bars you trade."""
    return _flip_nb(high, low, close, float(long_offset), float(short_offset))


# ---------------------------------------------------------------------------
# Volumatic VIDYA [BigBeluga]
# ---------------------------------------------------------------------------

@njit(cache=True)
def _bb_vidya_nb(src, cmo, alpha):
    out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        v1 = NAN
        for i in range(src.shape[0]):
            kk = alpha * cmo[i, c] / 100
            v = kk * src[i, c] + (1 - kk) * _nz(v1)
            out[i, c] = v
            v1 = v
    return out


@njit(cache=True)
def _bb_trend_nb(xu, xd, upper, lower):
    shape = upper.shape
    tr = np.zeros(shape, dtype=np.bool_)
    sm = np.full(shape, NAN)
    for c in range(shape[1]):
        up = False
        for i in range(shape[0]):
            prev = up
            if xu[i, c]:
                up = True
            if xd[i, c]:
                up = False
            tr[i, c] = up
            if i > 0 and up != prev:
                sm[i, c] = NAN
            else:
                sm[i, c] = lower[i, c] if up else upper[i, c]
    return tr, sm


@indicator("VOLUMATIC_VIDYA", ["high", "low", "close"], ["vidya", "upper", "lower", "trend_up", "trail"])
def volumatic_vidya(high, low, close, length=10, momentum=20, band_distance=2.0):
    """Volumatic Variable Index Dynamic Average [BigBeluga] (PUB;04a9de6f...),
    the trend part (the volume / liquidity labels are not reproduced).

    VIDYA with alpha = 2/(length+1) * |CMO(momentum)|/100, zero-seeded, then
    ``ta.sma(.., 15)``; bands -+ ATR(200)*band_distance. ``trend_up`` turns
    true on a close crossover of the upper band and false on a crossunder
    of the lower band (``var bool``, false at the start); ``trail`` is the
    lower band in an up trend, the upper band otherwise, NaN on the flip bar.
    """
    mom = change_2d(close)
    with np.errstate(invalid="ignore"):
        pos = k.sum_nb(np.where(mom >= 0, mom, 0.0), int(momentum))
        neg = k.sum_nb(np.where(mom >= 0, 0.0, -mom), int(momentum))
    cmo = np.abs(safe_div(100 * (pos - neg), pos + neg))
    v = k.sma_nb(_bb_vidya_nb(close, cmo, 2.0 / (length + 1)), 15)
    atr = atr_2d(high, low, close, 200)
    upper = v + atr * float(band_distance)
    lower = v - atr * float(band_distance)
    tr, sm = _bb_trend_nb(_xover(close, upper), _xunder(close, lower), upper, lower)
    return v, upper, lower, tr, sm


# ---------------------------------------------------------------------------
# Chande TrendScore
# ---------------------------------------------------------------------------

@indicator("TREND_SCORE", ["close"], ["score"])
def trend_score(close, from_index=11, to_index=20):
    """Tushar Chande's TrendScore ("Rating Trend Strength", TASC Sept 1993):
    sum over lags i = from..to of +1 if close >= close[i], else -1, so
    -10..+10 with Chande's 11..20. NaN until ``to_index`` bars of history;
    the FMZ copy uses ``nz(src[i])`` and so counts +1 for missing bars.
    """
    a, b = int(from_index), int(to_index)
    s = np.zeros(close.shape)
    with np.errstate(invalid="ignore"):
        for i in range(a, b + 1):
            s += np.where(close >= shift_2d(close, i), 1.0, -1.0)
    s[np.isnan(shift_2d(close, b)) | np.isnan(close)] = NAN
    return s


# ---------------------------------------------------------------------------
# Recursive Bands [alexgrover]
# ---------------------------------------------------------------------------

@njit(cache=True)
def _rfv_nb(src, n):
    out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        r = NAN
        for i in range(src.shape[0]):
            if i >= n:
                rising = True
                falling = True
                x = src[i, c]
                for j in range(1, n + 1):
                    p = src[i - j, c]
                    if not x > p:
                        rising = False
                    if not x < p:
                        falling = False
                if rising or falling:
                    r = abs(x - src[i - 1, c])
            out[i, c] = r
    return out


@njit(cache=True)
def _recursive_bands_nb(src, vol, sc, classic):
    a_o = np.full(src.shape, NAN)
    b_o = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        a1 = NAN
        b1 = NAN
        for i in range(src.shape[0]):
            s = src[i, c]
            pa = s if np.isnan(a1) else a1
            pb = s if np.isnan(b1) else b1
            va = abs(s - pa) if classic else vol[i, c]
            vb = abs(s - pb) if classic else vol[i, c]
            a = _max2(pa, s) - sc * va
            b = _min2(pb, s) + sc * vb
            a_o[i, c] = a
            b_o[i, c] = b
            a1 = a
            b1 = b
    return a_o, b_o


@indicator("RECURSIVE_BANDS", ["high", "low", "close"], ["upper", "lower", "middle"])
def recursive_bands(high, low, close, length=100, method="classic"):
    """(Extended) Recursive Bands [alexgrover] (PUB;qLuJ87gK9HlpqlLanJfXD0KcwwZejDzz).

    a = max(nz(a[1], src), src) - sc*v(|src - nz(a[1], src)|), b mirrored,
    sc = 2/(length+1). ``method``: "classic" (v(x) = x), "atr" (ATR(length)),
    "stdev", "ahlr" (SMA of high-low) or "rfv" (|change| at the last bar that
    was rising / falling over ``length`` bars). ``middle`` = (a+b)/2, the
    line FMZ's "Extended Recursive Bands Strategy" adds.
    """
    n = int(length)
    m = _norm(method)
    if m == "classic":
        vol = np.full(close.shape, NAN)
    elif m == "atr":
        vol = atr_2d(high, low, close, n)
    elif m == "stdev":
        vol = k.stdev_nb(close, n)
    elif m == "ahlr":
        vol = k.sma_nb(high - low, n)
    elif m == "rfv":
        vol = _rfv_nb(close, n)
    else:
        raise ValueError("method must be classic, atr, stdev, ahlr or rfv")
    a, b = _recursive_bands_nb(close, vol, 2.0 / (n + 1), m == "classic")
    return a, b, (a + b) / 2


# ---------------------------------------------------------------------------
# Adaptive least-squares trend ("OCC Trend Combo" functionTrend)
# ---------------------------------------------------------------------------

@njit(cache=True)
def _adaptive_ls_nb(close, n, sc):
    shape = close.shape
    b_o = np.full(shape, NAN)
    osc_o = np.full(shape, NAN)
    ls_o = np.full(shape, NAN)
    for c in range(shape[1]):
        sh = np.full(shape[0], NAN)
        bh = np.full(shape[0], NAN)
        ls1 = NAN
        b1 = NAN
        cum = 0.0
        alpha = NAN
        osc = NAN
        for i in range(shape[0]):
            x = close[i, c]
            s = sc * x + (1 - sc) * (x if np.isnan(ls1) else ls1)
            sh[i] = s
            er = NAN
            if i >= n:
                den = 0.0
                for j in range(n):
                    den += abs(sh[i - j] - sh[i - j - 1])
                if den != 0:
                    er = 1 - abs(s - sh[i - n]) / den
            pb = s if np.isnan(b1) else b1
            cum += abs(s - pb)
            a = cum / i * (1 + er) if i > 0 else NAN
            if s > pb + a:
                b = s
            elif s < pb - a:
                b = s
            else:
                b = pb
            bh[i] = b
            ls = NAN
            if i >= n - 1:
                ms = 0.0
                mb = 0.0
                for j in range(n):
                    ms += sh[i - j]
                    mb += bh[i - j]
                ms /= n
                mb /= n
                sxy = 0.0
                sxx = 0.0
                syy = 0.0
                for j in range(n):
                    dx = sh[i - j] - ms
                    dy = bh[i - j] - mb
                    if abs(dx) <= 1e-10:  # Pine's ta.stdev treats |dev| <= 1e-10 as 0
                        dx = 0.0
                    if abs(dy) <= 1e-10:
                        dy = 0.0
                    sxy += dx * dy
                    sxx += dx * dx
                    syy += dy * dy
                if sxx > 0 and syy > 0:
                    raw = sxy / np.sqrt(sxx * syy) * (np.sqrt(sxx / n) / np.sqrt(syy / n))
                    if not np.isnan(raw):
                        alpha = raw  # fixnan
                ls = alpha * b + (ms - alpha * mb)
            if b > b1:
                osc = 1.0
            elif b < b1:
                osc = 0.0
            b_o[i, c] = b
            osc_o[i, c] = osc
            ls_o[i, c] = ls
            ls1 = ls
            b1 = b
    return b_o, osc_o, ls_o


@indicator("ADAPTIVE_LS_TREND", ["close"], ["trail", "osc", "ls"])
def adaptive_ls_trend(close, length=24, sc=0.2):
    """``functionTrend`` of the FMZ "OCC Trend Combo" strategy (Josef Tainsh),
    strategy-specific; it reworks alexgrover's adaptive trailing level.

    src = sc*close + (1-sc)*ls[1]; the trailing level b jumps to src when src
    moves more than a = cum|src - b[1]| / bar_index * (1 + ER(length)) away;
    ls = least-squares fit of src on b over ``length`` bars (slope =
    correlation * stdev(src)/stdev(b), ``fixnan``). ``osc``: 1 when b last
    rose, 0 when it last fell. Chart-timeframe version (the script's
    ``security`` / ``is_newBar`` handling of a higher timeframe is left out:
    feed higher-timeframe bars to use one).
    """
    return _adaptive_ls_nb(close, int(length), float(sc))


# ---------------------------------------------------------------------------
# Small strategy-specific formulas
# ---------------------------------------------------------------------------

@indicator("LOGISTIC_PRICE_FORECAST", ["close", "volume"], ["forecast", "z"])
def logistic_price_forecast(close, volume, std_length=20, z_std_length=100, z_sma_length=10):
    """The FMZ "Logistic" strategy's forecast, strategy-specific.

    net volume = +volume on up closes, -volume otherwise;
    z = sma(net, 10) / stdev(net, 100); std = stdev(close, 20);
    forecast = (close + std) / (1 + (std/close) * exp(-z)).
    """
    with np.errstate(invalid="ignore"):
        net = np.where(close > shift_2d(close, 1), volume, -volume)
    z = safe_div(k.sma_nb(net, int(z_sma_length)), k.stdev_nb(net, int(z_std_length)))
    sd = k.stdev_nb(close, int(std_length))
    with np.errstate(over="ignore", invalid="ignore"):
        return (close + sd) / (1 + sd / close * np.exp(-z)), z


@njit(cache=True)
def _hold_on_change_nb(src, w):
    out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        h = NAN
        for i in range(src.shape[0]):
            if i > 0 and src[i, c] - src[i - 1, c] != 0 and not np.isnan(src[i, c] - src[i - 1, c]):
                h = w[i, c]
            out[i, c] = h
    return out


@indicator("ATR_ENVELOPE", ["source", "high", "low", "close"], ["upper", "lower"])
def atr_envelope(source, high, low, close, length=34, mult=3.0):
    """ATR envelope of "baguette by multigrain" (credited to redktrader),
    strategy-specific: source -+ ATR(length)*mult, where the width only
    updates on bars where the source changes. The strategy's source is a
    JMA(144, 34) of close (``fmz_catalog.extra.jma``)."""
    w = _hold_on_change_nb(source, atr_2d(high, low, close, int(length)) * float(mult))
    return source + w, source - w


@indicator("AVELLANEDA_STOIKOV_QUOTES", ["close"], ["bid", "ask", "mid"])
def avellaneda_stoikov_quotes(close, gamma=2.0, sigma=8.0, t=0.0833, k=5.0, fee=0.0, model="tamim",
                              inventory=0.0):
    """Bid / ask quotes.

    ``model="tamim"`` (default): "Khaled Tamim's Avellaneda-Stoikov Strategy",
    strategy-specific: mid = (close + close[1])/2, quotes
    mid -+ (k*gamma*sigma^2*T + mid*fee). That is not the real model.
    ``model="as2008"``: Avellaneda & Stoikov (2008), "High-frequency trading
    in a limit order book": reservation price r = close - q*gamma*sigma^2*T
    (q = ``inventory``), spread = gamma*sigma^2*T + (2/gamma)*ln(1 + gamma/k),
    quotes r -+ spread/2 (``mid`` = r).
    """
    g, s2, T = float(gamma), float(sigma) ** 2, float(t)
    if _norm(model) == "as2008":
        r = close - float(inventory) * g * s2 * T
        half = (g * s2 * T + 2 / g * math.log(1 + g / float(k))) / 2
        return r - half, r + half, r
    mid = (close + shift_2d(close, 1)) / 2
    term = float(k) * g * s2 * T
    return mid - term - mid * fee, mid + term + mid * fee, mid


@indicator("DUAL_THRUST", ["open", "high", "low", "close"], ["buy_trigger", "sell_trigger", "buy_range",
                                                             "sell_range"])
def dual_thrust(open, high, low, close, length=4, k1=0.5, k2=0.5, sell_length=0):
    """Dual Thrust (Michael Chalek): Range = max(HH - LC, HC - LL) over the
    previous ``length`` bars (current bar excluded); buy trigger =
    open + k1*Range, sell trigger = open - k2*Range. ``sell_length`` > 0 gives
    the sell side its own lookback (capissimo's "Algo #2").

    Chalek's system uses daily ranges and the day's open with intraday
    entries: compute it on daily bars and map with a higher-timeframe helper.
    Defaults are QuantConnect's tutorial (N=4, K1=K2=0.5); capissimo's
    script defaults to 5 / 14 with trend-dependent k.
    """
    def rng(n):
        hh = shift_2d(k.highest_nb(high, n), 1)
        hc = shift_2d(k.highest_nb(close, n), 1)
        lc = shift_2d(k.lowest_nb(close, n), 1)
        ll = shift_2d(k.lowest_nb(low, n), 1)
        return np.maximum(hh - lc, hc - ll)  # NaN when either side is NaN, like Pine's max

    br = rng(int(length))
    sr = rng(int(sell_length)) if int(sell_length) > 0 else br
    return open + float(k1) * br, open - float(k2) * sr, br, sr


@njit(cache=True)
def _see_nb(x, n):
    """Standard error of the estimate around the rolling least-squares line."""
    out = np.full(x.shape, NAN)
    sx = n * (n - 1) / 2.0
    sxx = (n - 1) * n * (2 * n - 1) / 6.0
    den = n * sxx - sx * sx
    for c in range(x.shape[1]):
        for i in range(n - 1, x.shape[0]):
            sy = 0.0
            sxy = 0.0
            for j in range(n):
                y = x[i - (n - 1) + j, c]
                sy += y
                sxy += j * y
            b = (n * sxy - sx * sy) / den
            a = (sy - b * sx) / n
            ss = 0.0
            for j in range(n):
                e = x[i - (n - 1) + j, c] - (a + b * j)
                ss += e * e
            out[i, c] = math.sqrt(ss / (n - 2))
    return out


@indicator("STANDARD_ERROR_BANDS", ["close"], ["middle", "upper", "lower", "see"])
def standard_error_bands(close, length=21, mult=2.0, smoothing=3):
    """Standard Error Bands (Jon Andersen, TASC Sept 1996).

    middle = SMA(linreg(close, length), smoothing); bands = SMA(linreg -+
    mult*SEE, smoothing), SEE = sqrt(sum of squared residuals / (n-2)) around
    the window's regression line. Capissimo's "Dual Thrust (ps4)" narrow band
    is this (with 20 / 2 / 3); its "wide" band is not a standard error.
    """
    n, s = int(length), int(smoothing)
    lr = k.linreg_nb(close, n, 0)
    see = _see_nb(close, n)
    return k.sma_nb(lr, s), k.sma_nb(lr + float(mult) * see, s), k.sma_nb(lr - float(mult) * see, s), see


@njit(cache=True)
def _atf_state_nb(close, basis, upper, lower):
    shape = close.shape
    tr_o = np.zeros(shape)
    lv_o = np.full(shape, NAN)
    for c in range(shape[1]):
        lvl = NAN
        tr = 0.0
        for i in range(shape[0]):
            cl = close[i, c]
            if np.isnan(lvl):
                tr = 1.0 if cl > basis[i, c] else -1.0
                lvl = lower[i, c] if tr == 1.0 else upper[i, c]
            if tr == 1.0:
                if cl < lower[i, c]:
                    tr = -1.0
                    lvl = upper[i, c]
                else:
                    lvl = lower[i, c]
            else:
                if cl > upper[i, c]:
                    tr = 1.0
                    lvl = lower[i, c]
                else:
                    lvl = upper[i, c]
            tr_o[i, c] = tr
            lv_o[i, c] = lvl
    return tr_o, lv_o


@indicator("ADAPTIVE_TREND_FLOW", ["high", "low", "close"], ["basis", "upper", "lower", "trend", "level"])
def adaptive_trend_flow(high, low, close, length=10, smooth_length=14, sensitivity=2.0):
    """Adaptive Trend Flow [QuantAlgo] (PUB;87158567b731451c8a1347f953921ab7).

    basis = (EMA(hlc3, n) + EMA(hlc3, 2n))/2, bands -+ EMA(stdev(hlc3, n),
    smooth)*sensitivity; ``trend`` flips when close crosses the opposite band
    and ``level`` is the band on the trend's side.
    """
    n = int(length)
    t = (high + low + close) / 3
    basis = (k.ema_nb(t, n) + k.ema_nb(t, 2 * n)) / 2
    sv = k.ema_nb(k.stdev_nb(t, n), int(smooth_length))
    upper = basis + sv * float(sensitivity)
    lower = basis - sv * float(sensitivity)
    tr, lvl = _atf_state_nb(close, basis, upper, lower)
    return basis, upper, lower, tr, lvl


@indicator("ANDEAN_OSCILLATOR", ["open", "close"], ["bull", "bear", "signal"])
def andean_oscillator(open, close, length=50, signal_length=9):
    """Andean Oscillator (alexgrover, 2022; alpaca.markets/learn article),
    used by FMZ's "Adaptive Trend Detection ... Dual Envelope EMA System".

    Exponential envelopes of price and price^2 that are pushed out by
    max/min(close, open); bull = sqrt(dn2 - dn1^2), bear = sqrt(up2 - up1^2)
    (NaN when rounding makes the variance negative, as in Pine);
    signal = EMA(max(bull, bear), signal_length). Seeded with close.
    """
    up1, up2, dn1, dn2 = _andean_nb(open, close, 2.0 / (length + 1))
    with np.errstate(invalid="ignore"):
        bull = np.sqrt(dn2 - dn1 * dn1)
        bear = np.sqrt(up2 - up1 * up1)
    return bull, bear, k.ema_nb(np.maximum(bull, bear), int(signal_length))


@njit(cache=True)
def _andean_nb(open_, close, alpha):
    shape = close.shape
    o0 = np.full(shape, NAN)
    o1 = np.full(shape, NAN)
    o2 = np.full(shape, NAN)
    o3 = np.full(shape, NAN)
    for c in range(shape[1]):
        u1 = NAN
        u2 = NAN
        d1 = NAN
        d2 = NAN
        for i in range(shape[0]):
            C = close[i, c]
            O = open_[i, c]
            v = _max2(_max2(C, O), u1 - (u1 - C) * alpha)
            u1 = C if np.isnan(v) else v
            v = _max2(_max2(C * C, O * O), u2 - (u2 - C * C) * alpha)
            u2 = C * C if np.isnan(v) else v
            v = _min2(_min2(C, O), d1 + (C - d1) * alpha)
            d1 = C if np.isnan(v) else v
            v = _min2(_min2(C * C, O * O), d2 + (C * C - d2) * alpha)
            d2 = C * C if np.isnan(v) else v
            o0[i, c] = u1
            o1[i, c] = u2
            o2[i, c] = d1
            o3[i, c] = d2
    return o0, o1, o2, o3


# ---------------------------------------------------------------------------
# LuxAlgo: Fibonacci Progression With Breaks, SuperIchi
# ---------------------------------------------------------------------------

@njit(cache=True)
def _fibprog_nb(src, atr, size, mx, use_atr):
    shape = src.shape
    fib = np.ones(mx + 2)
    for i in range(1, mx + 1):
        fib[i + 1] = fib[i - 1] + fib[i]
    avg_o = np.full(shape, NAN)
    dist_o = np.full(shape, NAN)
    os_o = np.zeros(shape)
    tp_o = np.full(shape, NAN)
    sl_o = np.full(shape, NAN)
    fn_o = np.zeros(shape)
    for c in range(shape[1]):
        avg = 0.0
        a1 = NAN
        fn = 1
        os = 0.0
        for i in range(shape[0]):
            s = src[i, c]
            dist = (atr[i, c] if use_atr else 1.0) * size * fib[fn]
            if abs(s - avg) > dist:
                fn += 1
            v = s if fn > mx + 1 else a1
            avg = s if np.isnan(v) else v
            if fn > mx + 1:
                fn = 1
            if avg > a1:
                os = 1.0
            elif avg < a1:
                os = 0.0
            if not (avg != a1 and not np.isnan(a1)):
                tp_o[i, c] = avg + dist if os == 1.0 else avg - dist
                sl_o[i, c] = avg + dist if os == 0.0 else avg - dist
            avg_o[i, c] = avg
            dist_o[i, c] = dist
            os_o[i, c] = os
            fn_o[i, c] = fn
            a1 = avg
    return avg_o, dist_o, os_o, tp_o, sl_o, fn_o


@indicator("FIB_PROGRESSION_BREAKS", ["high", "low", "close"],
           ["avg", "dist", "os", "buy", "sell", "target", "stop", "fib_n"])
def fib_progression_breaks(high, low, close, method="atr", size=1.0, sequence_length=3):
    """Fibonacci Progression With Breaks [LuxAlgo] (PUB;91fffae7...).

    A central level ``avg`` resets to the close once price has moved more than
    dist = ATR(200)*size*fib[n] (``method="manual"``: size*fib[n]) away
    ``sequence_length`` + 1 times in a row, n stepping along 1, 1, 2, 3, 5...
    ``buy`` / ``sell``: avg reset up / down; ``os`` 1 / 0 the last direction;
    ``target`` / ``stop`` = avg -+ dist (NaN on reset bars).
    """
    use_atr = _norm(method) == "atr"
    atr = atr_2d(high, low, close, 200) if use_atr else np.ones(close.shape)
    avg, dist, os, tp, sl, fn = _fibprog_nb(close, atr, float(size), int(sequence_length), use_atr)
    a1 = shift_2d(avg, 1)
    with np.errstate(invalid="ignore"):
        return avg, dist, os, avg > a1, avg < a1, tp, sl, fn


@njit(cache=True)
def _superichi_nb(src, hl2, atr):
    shape = src.shape
    out = np.full(shape, NAN)
    for c in range(shape[1]):
        upper1 = NAN
        lower1 = NAN
        os = NAN
        max1 = NAN
        min1 = NAN
        spt1 = NAN
        s1 = NAN
        for i in range(shape[0]):
            s = src[i, c]
            up = hl2[i, c] + atr[i, c]
            dn = hl2[i, c] - atr[i, c]
            upper = _min2(up, upper1) if s1 < upper1 else up
            lower = _max2(dn, lower1) if s1 > lower1 else dn
            if s > upper:
                os = 1.0
            elif s < lower:
                os = 0.0
            spt = lower if os == 1.0 else upper
            cross = (s > spt and s1 <= spt1) or (s < spt and s1 >= spt1)
            if cross or os == 1.0:
                mx = _max2(s, max1)
            else:
                mx = spt
            if cross or os == 0.0:
                mn = _min2(s, min1)
            else:
                mn = spt
            out[i, c] = (mx + mn) / 2
            upper1 = upper
            lower1 = lower
            max1 = mx
            min1 = mn
            spt1 = spt
            s1 = s
    return out


@indicator("SUPERICHI", ["high", "low", "close"],
           ["tenkan", "kijun", "senkou_a", "senkou_b", "cloud_a", "cloud_b"])
def superichi(high, low, close, tenkan_len=9, tenkan_mult=2.0, kijun_len=26, kijun_mult=4.0, spanb_len=52,
              spanb_mult=6.0, offset=26):
    """SuperIchi [LuxAlgo] (PUB;ec52552d888e467b9e25df03bad61c85): Ichimoku
    lines built from the running max / min of close tracked against a
    SuperTrend (ATR(len)*mult around hl2).

    ``senkou_a`` = (tenkan + kijun)/2 and ``senkou_b`` are the values computed
    on the current bar; the script plots them ``offset - 1`` bars ahead, so
    the cloud under the current bar is ``cloud_a`` / ``cloud_b``
    (= senkou[offset-1]). The Chikou line (close shifted back) is left out:
    it is look-ahead.
    """
    hl2 = (high + low) / 2
    lines = [_superichi_nb(close, hl2, atr_2d(high, low, close, int(n)) * float(m))
             for n, m in ((tenkan_len, tenkan_mult), (kijun_len, kijun_mult), (spanb_len, spanb_mult))]
    ten, kij, sb = lines
    sa = (kij + ten) / 2
    return ten, kij, sa, sb, shift_2d(sa, int(offset) - 1), shift_2d(sb, int(offset) - 1)


# ---------------------------------------------------------------------------
# [CS] AMA Channel Break Out (adaptive MA channel)
# ---------------------------------------------------------------------------

@njit(cache=True)
def _ama_channel_nb(price, snrf, p, beta):
    shape = price.shape
    ama_o = np.full(shape, NAN)
    hb_o = np.full(shape, NAN)
    lb_o = np.full(shape, NAN)
    al_o = np.full(shape, NAN)
    fast = p // 2
    an = 2.0 * (p - 1) / (p - 2.0) if p > 2 else NAN  # lambda = p / (p/2) = 2
    pi2 = 1.5707963267948966
    for c in range(shape[1]):
        nat = np.full(shape[0], NAN)
        av1 = np.full(shape[0], NAN)
        al1 = NAN
        ama1 = NAN
        dmax1 = NAN
        dmin1 = NAN
        bhb1 = NAN
        blb1 = NAN
        for i in range(shape[0]):
            x = price[i, c]
            x1 = price[i - 1, c] if i > 0 else NAN
            ama = al1 * x + (1 - al1) * _nz(ama1)
            ret = (x - x1) / x1
            dmax = al1 * _max2(ret, 0.0) + (1 - al1) * _nz(dmax1)
            dmin = -al1 * _min2(ret, 0.0) + (1 - al1) * _nz(dmin1)
            bhb = beta * dmax
            blb = beta * dmin
            hb = (1 + bhb1) * ama
            lb = (1 - blb1) * ama
            if x > hb:
                snr = ((x - ama1) / ama1) / blb if blb != 0 and ama1 != 0 else NAN
            elif x < lb:
                snr = -((x - ama1) / ama1) / bhb if bhb != 0 and ama1 != 0 else NAN
            else:
                snr = 0.0
            nat[i] = (math.atan(snrf * snr) + pi2) / (2 * pi2)
            if i >= p - 1:
                s = 0.0
                for j in range(p):
                    s += nat[i - j] * (p - j)
                av1[i] = s / (p * (p + 1) / 2.0)
            al = NAN
            if i >= fast - 1 and fast >= 1:
                s = 0.0
                for j in range(fast):
                    s += av1[i - j] * (fast - j)
                av2 = s / (fast * (fast + 1) / 2.0)
                al = (1 + an) * av1[i] - an * av2
            ama_o[i, c] = ama
            hb_o[i, c] = hb
            lb_o[i, c] = lb
            al_o[i, c] = al
            al1 = al
            ama1 = ama
            dmax1 = dmax
            dmin1 = dmin
            bhb1 = bhb
            blb1 = blb
    return ama_o, hb_o, lb_o, al_o


@indicator("AMA_CHANNEL", ["close"], ["ama", "upper", "lower", "alpha"])
def ama_channel(close, snr_factor=2.1, lookback=5, beta=2.1):
    """"[CS] AMA Strategy - Channel Break Out" (FMZ "Adaptive Moving Average
    Channel Breakout"), strategy-specific.

    ama = alpha[1]*price + (1-alpha[1])*ama[1] (zero-seeded); the channel is
    ama*(1 + beta*EMA of positive returns) / ama*(1 - beta*EMA of negative
    returns), both EMAs using alpha[1]; alpha is Duerschner's NWMA of
    (atan(snr_factor*SNR) + pi/2)/pi, SNR = breakout size over the band
    width. Pine's int/float division in the NWMA gives lambda = 2 for every
    lookback >= 4.
    """
    return _ama_channel_nb(close, float(snr_factor), int(lookback), float(beta))


# ---------------------------------------------------------------------------
# Trend persistence (VAWSI script), RSI Trend Reversal threshold
# ---------------------------------------------------------------------------

@njit(cache=True)
def _hi_custom(h, i, n):
    """``highest_custom(src, length)`` of the FMZ VAWSI / RSI Trend Reversal
    scripts: max of src[0..length] (length + 1 bars), skipping NaN history."""
    x = h[i]
    for j in range(0, min(n, 4999) + 1):
        if i - j < 0:
            break
        if h[i - j] > x:
            x = h[i - j]
    return x


@njit(cache=True)
def _lo_custom(h, i, n):
    x = h[i]
    for j in range(0, min(n, 4999) + 1):
        if i - j < 0:
            break
        if h[i - j] < x:
            x = h[i - j]
    return x


@njit(cache=True)
def _wma_at(h, i, n):
    if i - n + 1 < 0:
        return NAN
    s = 0.0
    for j in range(n):
        s += h[i - j] * (n - j)
    return s / (n * (n + 1) / 2.0)


@njit(cache=True)
def _trend_persistence_nb(src, length, sm):
    shape = src.shape
    out = np.full(shape, NAN)
    for c in range(shape[1]):
        nb = shape[0]
        tu = np.full(nb, NAN)
        td = np.full(nb, NAN)
        tu2 = np.full(nb, NAN)
        td2 = np.full(nb, NAN)
        mx = np.full(nb, NAN)
        tr = np.full(nb, NAN)
        h = src[:, c].copy()
        cu = NAN
        cd = NAN
        up = NAN
        dn = NAN
        for i in range(nb):
            ln = length[i, c]
            n = int(ln) if not np.isnan(ln) else 0
            tu[i] = abs(h[i] - _hi_custom(h, i, n))
            td[i] = abs(h[i] - _lo_custom(h, i, n))
            wu = _wma_at(tu, i, sm)
            wd = _wma_at(td, i, sm)
            pcu = cu
            pcd = cd
            if not np.isnan(wu):
                cu = wu if np.isnan(cu) else cu + wu
            if not np.isnan(wd):
                cd = wd if np.isnan(cd) else cd + wd
            tu2[i] = cu - pcu
            td2[i] = cd - pcd
            mx[i] = _max2(tu2[i], td2[i])
            tr[i] = _wma_at(mx, i, sm)
            ch = tr[i] - tr[i - 1] if i > 0 else NAN
            if n < 1:
                up = NAN
                dn = NAN
            else:
                up = _nz(up) * (n - 1) / n + _max2(ch, 0.0) / n
                dn = _nz(dn) * (n - 1) / n + (-_min2(ch, 0.0)) / n
            out[i, c] = 100 - 100 / (1 + up / dn) if dn != 0 else NAN
    return out


@indicator("TREND_PERSISTENCE", ["close", "length"], ["trend_persistence"])
def trend_persistence(close, length=14, smoothing=3):
    """``trendPersistence`` of the FMZ "VAWSI and Trend Persistence Reversal"
    strategy, strategy-specific: an RSI of how far price stays from its
    rolling extremes.

    trendu/d = |src - highest/lowest_custom(src, length)| (length + 1 bars),
    WMA(smoothing), then change(cum()), WMA of their max, then RSI with the
    script's zero-seeded Wilder average. ``length`` may be a series (the
    strategy feeds BlackCat1402's Ehlers dominant-cycle length).
    """
    return _trend_persistence_nb(close, length, int(smoothing))


@njit(cache=True)
def _rsi_thresh_nb(src, rsi, atr, mult, sl, tp):
    shape = src.shape
    th_o = np.full(shape, NAN)
    dir_o = np.full(shape, NAN)
    for c in range(shape[1]):
        nb = shape[0]
        s = src[:, c].copy()
        x1 = np.full(nb, NAN)
        y1 = np.full(nb, NAN)
        x2 = np.full(nb, NAN)
        z2 = np.full(nb, NAN)
        xu = False
        xd = False
        last = -1
        bear = 0.0
        d = NAN
        th = NAN
        for i in range(nb):
            if xu or xd:
                last = i
            if last < 0:
                bear += 1
            else:
                bear = float(i - last)
            n = int(bear)
            rl = rsi[i, c]
            ru = abs(rsi[i, c] - 100)
            an = atr[i, c] / s[i]
            x1[i] = _hi_custom(s, i, n) * (1 - (an + (1 / rl * mult if rl != 0 else NAN)))
            y1[i] = _max2(_hi_custom(x1, i, n), s[i] * sl)
            lower = _hi_custom(y1, i, n)
            x2[i] = _lo_custom(s, i, n) * (1 + (an + (1 / ru * mult if ru != 0 else NAN)))
            z2[i] = _min2(_lo_custom(x2, i, n), s[i] * tp)
            upper = _lo_custom(z2, i, n)
            prev_th = th
            if np.isnan(th):
                th = lower
            if np.isnan(d):
                d = 1.0
            if xd:
                d = -1.0
            if xu:
                d = 1.0
            if d == 1.0:
                th = lower
            if d == -1.0:
                th = upper
            s1 = s[i - 1] if i > 0 else NAN
            xu = s[i] > th and s1 <= prev_th
            xd = s[i] < th and s1 >= prev_th
            th_o[i, c] = th
            dir_o[i, c] = d
    return th_o, dir_o


@indicator("RSI_TREND_THRESHOLD", ["source", "high", "low", "close"], ["threshold", "direction"])
def rsi_trend_threshold(source, high, low, close, length=8, mult=1.5, min_diff=10.0):
    """``rsilev`` of the FMZ "RSI Trend Reversal" strategy, strategy-specific.

    A stop-and-reverse threshold: below price it is the highest of
    highest(src)*(1 - (ATR/src + mult/RSI)) and src*(1 - min_diff%) over the
    bars since the last cross; above price it mirrors with RSI' = 100 - RSI.
    The strategy feeds a Heikin-Ashi close as ``source`` (ATR uses the
    chart's high / low / close). ``direction`` 1 / -1.
    """
    n = int(length)
    return _rsi_thresh_nb(source, rsi_2d(source, n), atr_2d(high, low, close, n), float(mult),
                          (100 - float(min_diff)) / 100, (100 + float(min_diff)) / 100)


# ---------------------------------------------------------------------------
# Twin range filter trailing band, Trend Thrust Indicator
# ---------------------------------------------------------------------------

@njit(cache=True)
def _trf_nb(close, str_, sts):
    shape = close.shape
    fub_o = np.full(shape, NAN)
    flb_o = np.full(shape, NAN)
    trf_o = np.full(shape, NAN)
    for c in range(shape[1]):
        fub1 = NAN
        flb1 = NAN
        trf1 = NAN
        for i in range(shape[0]):
            c1 = close[i - 1, c] if i > 0 else NAN
            cl = close[i, c]
            pf = _nz(fub1)
            fub = str_[i, c] if (str_[i, c] < pf or c1 > pf) else pf
            pl = _nz(flb1)
            flb = sts[i, c] if (sts[i, c] > pl or c1 < pl) else pl
            pt = _nz(trf1)
            if pt == fub1 and cl <= fub:
                trf = fub
            elif pt == fub1 and cl >= fub:
                trf = flb
            elif pt == flb1 and cl >= flb:
                trf = flb
            elif pt == flb1 and cl <= flb:
                trf = fub
            else:
                trf = fub
            fub_o[i, c] = fub
            flb_o[i, c] = flb
            trf_o[i, c] = trf
            fub1 = fub
            flb1 = flb
            trf1 = trf
    return fub_o, flb_o, trf_o


@indicator("RANGE_FILTER_TRAILING", ["close"], ["filter", "upper", "lower", "trail"])
def range_filter_trailing(close, fast_period=27, fast_range=1.6, slow_period=55, slow_range=2.0):
    """Twin Range Filter [colinmck] with the SuperTrend-style trailing band
    of the FMZ "Dual Range Filter Momentum" strategy (FUB / FLB / TRF),
    strategy-specific.

    upper = filter + range, kept unless it falls or close[1] broke above it;
    lower mirrored; ``trail`` sits on the upper band while price is below it
    and switches to the lower band once close reaches the upper (and back).
    """
    r = (_smooth_range(close, fast_period, fast_range) + _smooth_range(close, slow_period, slow_range)) / 2
    f = _range_filter_nb(close, r)[0]
    fub, flb, trf = _trf_nb(close, f + r, f - r)
    return f, fub, flb, trf


@indicator("TREND_THRUST_INDICATOR", ["close", "volume"], ["tti", "signal"])
def trend_thrust_indicator(close, volume, fast=13, slow=26, signal=9):
    """Trend Thrust Indicator (Buff Pelz Dormeier, TASC Aug 2011; PineCodersTASC
    "TASC 2024.08 Volume Confirmation For A Trend System",
    PUB;76bb266d420a42d981b331c36106b2db).

    vMult = (VWMA(fast)/VWMA(slow))^2; TTI = VWMA(fast)*vMult - VWMA(slow)/vMult;
    signal = SMA(TTI, signal).
    """
    f = ma_2d(close, int(fast), "vwma", volume)
    s = ma_2d(close, int(slow), "vwma", volume)
    vm = safe_div(f, s) ** 2
    tti = f * vm - safe_div(s, vm)
    return tti, k.sma_nb(tti, int(signal))


# Keep these out of tv_indicators' registry so the main library is unchanged.
EXTRA_TREND = {name: REGISTRY.pop(name) for name in list(REGISTRY) if name not in _BEFORE}

__all__ = sorted(fn.__name__ for fn in EXTRA_TREND.values())
