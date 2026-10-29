"""Staging area: TradingView built-ins that FMZ strategies use and
``tv_indicators`` lacks, ported from TradingView's own published Pine source.

Like ``fmz_catalog.extra``, importing this module moves its indicators out of
the main registry into ``EXTRA_TV``, so ``tv_indicators`` is unchanged.

Sources (pine-facade ``https://pine-facade.tradingview.com/pine-facade/get/<id>/last``,
which returns the same text as the chart's "Source code" button):

* ``pivothigh`` / ``pivotlow``: ``ta.pivothigh`` / ``ta.pivotlow``. The Pine v6
  reference only says "returns price of the pivot high point, NaN if there
  was no pivot high point". It gives no tie rule. The rule used here is the
  one TradingView documents in its own ZigZag library
  (``import TradingView/ZigZag/9``, ``PUB;e875556fa20d4308ac8f0b31b27ca7e8``,
  ``findPivotPoint``): strictly beyond the older (left) bars, at least equal
  to the newer (right) bars.
* ``divergence`` / ``rsi_divergence``: "RSI divergence indicator",
  ``STD;Divergence%1Indicator`` (v37).
* ``candlestick_patterns``: "All candlestick patterns",
  ``STD;Candlestick%1Pattern%1All%1Candlestick%1Patterns`` (v38). Its
  definitions match the single-pattern scripts
  (``STD;Candlestick%1Pattern%1Bullish%1Engulfing`` and the others).
  ``inside_bar`` comes from ``STD;InSide%1Bar%1Strategy``. ``pin_bar`` is not
  a TradingView built-in.
* ``zigzag``: "Zigzag", ``STD;Zig_Zag`` (v44), which calls ``ZigZag.update()``
  from the TradingView/ZigZag/9 library.
* ``linreg_channel``: "Linear regression channel", ``STD;Linear_Regression`` (v31).
* ``htf`` / ``resample_ohlcv``: ``request.security`` timing as described in the
  Pine v6 User Manual, "Other timeframes and data".

    import fmz_catalog.extra_tv as xt
    ph = xt.pivothigh(df.high, 10, 10)
    cp = xt.candlestick_patterns(df.open, df.high, df.low, df.close)
"""

import numpy as np
import pandas as pd
from numba import njit

from tv_indicators import kernels as k
from tv_indicators._core import REGISTRY, indicator, shift_2d
from tv_indicators.oscillators import rsi_2d

NAN = np.nan
_BEFORE = set(REGISTRY)


# ---------------------------------------------------------------------------
# ta.pivothigh / ta.pivotlow
# ---------------------------------------------------------------------------

@njit(cache=True)
def _pivot_nb(x, left, right, sign, strict):
    """Pivot of ``sign * x`` confirmed ``right`` bars later.

    Left (older) bars must be strictly lower. Right (newer) bars must be
    lower or equal, or strictly lower when ``strict``. A window with a NaN
    gives no pivot.
    """
    out = np.full(x.shape, NAN)
    flag = np.zeros(x.shape, dtype=np.bool_)
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
                    if np.isnan(v) or sign * v > sp or (strict and sign * v == sp):
                        ok = False
                        break
            if ok:
                out[i, c] = p
                flag[i, c] = True
    return out, flag


@indicator("PIVOT_HIGH", ["high"], ["pivot", "found"])
def pivothigh(high, leftbars=10, rightbars=10, strict=False):
    """``ta.pivothigh(src, leftbars, rightbars)``, reported on the confirmation bar.

    ``pivot`` holds the pivot value on the bar ``rightbars`` after the pivot
    bar (the bar where Pine returns it) and NaN elsewhere. ``found`` is the
    same as a bool. The pivot bar is ``rightbars`` bars back. TradingView's
    "Pivot points high low" draws the label there with ``bar_index[rightbars]``.

    Tie rule (TradingView/ZigZag/9 ``findPivotPoint``): the pivot must be
    strictly above each of the ``leftbars`` older values and above or equal
    to each of the ``rightbars`` newer values. In a flat top the earliest bar
    is the pivot. ``strict=True`` also rejects ties on the right. A window
    that contains NaN gives no pivot. Defaults are those of "Pivot points
    high low" (10/10). Any source works (``high``, an oscillator, ...).
    """
    return _pivot_nb(high, int(leftbars), int(rightbars), 1.0, bool(strict))


@indicator("PIVOT_LOW", ["low"], ["pivot", "found"])
def pivotlow(low, leftbars=10, rightbars=10, strict=False):
    """``ta.pivotlow(src, leftbars, rightbars)``, reported on the confirmation bar.

    Mirror of ``pivothigh``: strictly below each of the ``leftbars`` older
    values and below or equal to each of the ``rightbars`` newer values.
    """
    return _pivot_nb(low, int(leftbars), int(rightbars), -1.0, bool(strict))


# ---------------------------------------------------------------------------
# RSI divergence indicator (TradingView built-in), any oscillator
# ---------------------------------------------------------------------------

@njit(cache=True)
def _divergence_nb(osc, high, low, pl, ph, lbr, rng_lo, rng_hi):
    shape = osc.shape
    bull = np.zeros(shape, dtype=np.bool_)
    hbull = np.zeros(shape, dtype=np.bool_)
    bear = np.zeros(shape, dtype=np.bool_)
    hbear = np.zeros(shape, dtype=np.bool_)
    for c in range(shape[1]):
        last_pl = -1      # last bar with plFound, before the current bar
        last_ph = -1
        pl_osc0 = NAN     # ta.valuewhen(plFound, osc[lbR], 0)
        pl_osc1 = NAN     # ... occurrence 1
        pl_low0 = NAN
        pl_low1 = NAN
        ph_osc0 = NAN
        ph_osc1 = NAN
        ph_high0 = NAN
        ph_high1 = NAN
        for i in range(shape[0]):
            o = osc[i - lbr, c] if i >= lbr else NAN
            lo = low[i - lbr, c] if i >= lbr else NAN
            hi = high[i - lbr, c] if i >= lbr else NAN
            # _inRange(plFound[1]): barssince(plFound[1]) = i - (last_pl + 1)
            in_pl = False
            if last_pl >= 0:
                bars = i - (last_pl + 1)
                in_pl = rng_lo <= bars and bars <= rng_hi
            in_ph = False
            if last_ph >= 0:
                bars = i - (last_ph + 1)
                in_ph = rng_lo <= bars and bars <= rng_hi
            if pl[i, c]:
                pl_osc1 = pl_osc0
                pl_low1 = pl_low0
                pl_osc0 = o
                pl_low0 = lo
            if ph[i, c]:
                ph_osc1 = ph_osc0
                ph_high1 = ph_high0
                ph_osc0 = o
                ph_high0 = hi
            if pl[i, c]:
                bull[i, c] = (lo < pl_low1) and (o > pl_osc1 and in_pl)
                hbull[i, c] = (lo > pl_low1) and (o < pl_osc1 and in_pl)
                last_pl = i
            if ph[i, c]:
                bear[i, c] = (hi > ph_high1) and (o < ph_osc1 and in_ph)
                hbear[i, c] = (hi < ph_high1) and (o > ph_osc1 and in_ph)
                last_ph = i
    return bull, hbull, bear, hbear


def _divergence_2d(osc, high, low, lbl, lbr, rng_hi, rng_lo):
    lbl, lbr = int(lbl), int(lbr)
    _, pl = _pivot_nb(osc, lbl, lbr, -1.0, False)
    _, ph = _pivot_nb(osc, lbl, lbr, 1.0, False)
    return _divergence_nb(osc, high, low, pl, ph, lbr, float(rng_lo), float(rng_hi)) + (pl, ph)


@indicator("DIVERGENCE", ["osc", "high", "low"],
           ["bull", "hidden_bull", "bear", "hidden_bear", "pivot_low", "pivot_high"])
def divergence(osc, high, low, lookback_left=5, lookback_right=5, range_upper=60, range_lower=5):
    """TradingView's "RSI divergence indicator" for any oscillator series.

    Port of ``STD;Divergence%1Indicator``. Oscillator pivots come from
    ``ta.pivotlow/pivothigh(osc, lbL, lbR)``. The previous pivot comes from
    ``ta.valuewhen(..., 1)``, and its distance is checked with
    ``rangeLower <= ta.barssince(plFound[1]) <= rangeUpper``.

    * bull: price ``low[lbR]`` lower low, osc higher low (regular bullish)
    * hidden_bull: price higher low, osc lower low
    * bear: price ``high[lbR]`` higher high, osc lower high (regular bearish)
    * hidden_bear: price lower high, osc higher high

    Delay: a signal is set on the confirmation bar, ``lookback_right`` bars
    after the pivot. That is where the script's ``alertcondition`` fires.
    TradingView draws the label ``lookback_right`` bars back
    (``offset=-lbR``). ``pivot_low``/``pivot_high`` are ``plFound``/``phFound``.
    The "Plot ..." toggles only hide plots, so all four signals are returned.
    """
    return _divergence_2d(osc, high, low, lookback_left, lookback_right, range_upper, range_lower)


@indicator("RSI_DIVERGENCE", ["close", "high", "low"],
           ["bull", "hidden_bull", "bear", "hidden_bear", "pivot_low", "pivot_high"])
def rsi_divergence(close, high, low, length=14, lookback_left=5, lookback_right=5,
                   range_upper=60, range_lower=5):
    """The built-in exactly: ``divergence(ta.rsi(close, 14), high, low)``."""
    return _divergence_2d(rsi_2d(close, int(length)), high, low, lookback_left,
                          lookback_right, range_upper, range_lower)


# ---------------------------------------------------------------------------
# Candlestick patterns (TradingView built-ins)
# ---------------------------------------------------------------------------

_CANDLE_OUTPUTS = [
    "on_neck_bear", "rising_window_bull", "falling_window_bear",
    "falling_three_methods_bear", "rising_three_methods_bull",
    "tweezer_top_bear", "tweezer_bottom_bull", "dark_cloud_cover_bear",
    "downside_tasuki_gap_bear", "upside_tasuki_gap_bull",
    "evening_doji_star_bear", "doji_star_bear", "doji_star_bull",
    "morning_doji_star_bull", "piercing_bull", "hammer_bull",
    "hanging_man_bear", "shooting_star_bear", "inverted_hammer_bull",
    "morning_star_bull", "evening_star_bear", "marubozu_white_bull",
    "marubozu_black_bear", "doji", "gravestone_doji_bear",
    "dragonfly_doji_bull", "harami_cross_bull", "harami_cross_bear",
    "harami_bull", "harami_bear", "long_lower_shadow_bull",
    "long_upper_shadow_bear", "spinning_top_white", "spinning_top_black",
    "three_white_soldiers_bull", "three_black_crows_bear", "engulfing_bull",
    "engulfing_bear", "abandoned_baby_bull", "abandoned_baby_bear",
    "tri_star_bull", "tri_star_bear", "kicking_bull", "kicking_bear",
    "inside_bar", "pin_bar_bull", "pin_bar_bear",
]

_TREND_RULES = {"sma50": 1, "sma50, sma200": 2, "sma50,sma200": 2, "sma50+sma200": 2,
                "no detection": 0, "none": 0}


def _sb(x, n):
    """``boolSeries[n]``: Pine v6 bools are never na, so history before bar 0 is false."""
    out = np.zeros(x.shape, dtype=bool)
    out[n:] = x[:-n]
    return out


@indicator("CANDLESTICK_PATTERNS", ["open", "high", "low", "close"], _CANDLE_OUTPUTS)
def candlestick_patterns(open, high, low, close, trend_rule="SMA50", body_length=14,
                         shadow_percent=5.0, shadow_equals_percent=100.0,
                         doji_body_percent=5.0, factor=2.0, pin_ratio=2.0 / 3.0):
    """TradingView's candlestick pattern built-ins, one bool output per pattern.

    Port of "All candlestick patterns"
    (``STD;Candlestick%1Pattern%1All%1Candlestick%1Patterns``). The single
    pattern scripts share the same definitions. Each flag is True on the
    pattern's last candle, which is where TradingView puts the label.
    Multi-candle patterns look only at past bars, so there is no look-ahead.

    * ``trend_rule``: "SMA50" (default; down = close < SMA50), "SMA50, SMA200"
      (down = close < SMA50 < SMA200), or "No detection" (trend always true).
      SMA warm-up bars give no trend, so trend-filtered patterns are false there.
    * body average = ``ta.ema(body, 14)``, small/long body = below/above it.
      Has-shadow = shadow > 5% of body, doji body <= 5% of range, and hammer
      family shadow >= 2 x body. Marubozu shadows are <= 5% of body, long
      shadows > 75% of range, spinning-top shadows >= 34% of range, and the
      tweezer/on-neck tolerance is 5% of the body average.
    * ``doji`` is the labelled Doji: ``C_Doji and not dragonfly and not gravestone``.
    * ``inside_bar``: ``high < high[1] and low > low[1]``, from TradingView's
      "Inside bar strategy" (``STD;InSide%1Bar%1Strategy``).
    * ``pin_bar_bull`` / ``pin_bar_bear`` are **not TradingView built-ins**.
      They are a simple rule: range > 0 and the lower (upper) shadow is at
      least ``pin_ratio`` (2/3) of the range.
    """
    try:
        rule = _TREND_RULES[str(trend_rule).strip().lower()]
    except KeyError:
        raise ValueError(f"trend_rule must be 'SMA50', 'SMA50, SMA200' or 'No detection', not {trend_rule!r}")
    o, h, l, c = open, high, low, close

    def f(x, n):
        return shift_2d(x, n)

    with np.errstate(invalid="ignore", divide="ignore"):
        if rule == 1:
            avg = k.sma_nb(c, 50)
            down, up = c < avg, c > avg
        elif rule == 2:
            s200, s50 = k.sma_nb(c, 200), k.sma_nb(c, 50)
            down = (c < s50) & (s50 < s200)
            up = (c > s50) & (s50 > s200)
        else:
            down = np.ones(c.shape, dtype=bool)
            up = np.ones(c.shape, dtype=bool)

        body_hi = np.maximum(c, o)
        body_lo = np.minimum(c, o)
        body = body_hi - body_lo
        body_avg = k.ema_nb(body, int(body_length))
        small = body < body_avg
        long_ = body > body_avg
        up_sh = h - body_hi
        dn_sh = body_lo - l
        has_up = up_sh > shadow_percent / 100 * body
        has_dn = dn_sh > shadow_percent / 100 * body
        white = o < c
        black = o > c
        rng = h - l
        body_mid = body / 2 + body_lo
        r1 = np.abs(up_sh - dn_sh) / dn_sh * 100
        r2 = np.abs(dn_sh - up_sh) / up_sh * 100
        shadow_eq = (up_sh == dn_sh) | ((r1 < shadow_equals_percent) & (r2 < shadow_equals_percent))
        doji_body = (rng > 0) & (body <= rng * doji_body_percent / 100)
        doji_c = doji_body & shadow_eq
        hl2 = (h + l) / 2
        nz_rng = rng != 0

        out = {}
        out["on_neck_bear"] = (down & _sb(black, 1) & _sb(long_, 1) & white & (o < f(c, 1)) & small
                               & nz_rng & (np.abs(c - f(l, 1)) <= body_avg * 0.05))
        out["rising_window_bull"] = _sb(up, 1) & nz_rng & (f(rng, 1) != 0) & (l > f(h, 1))
        out["falling_window_bear"] = _sb(down, 1) & nz_rng & (f(rng, 1) != 0) & (h < f(l, 1))
        ftm = _sb(down, 4) & _sb(long_, 4) & _sb(black, 4)
        rtm = _sb(up, 4) & _sb(long_, 4) & _sb(white, 4)
        for j in (3, 2, 1):
            ftm &= _sb(small, j) & _sb(white, j) & (f(o, j) > f(l, 4)) & (f(c, j) < f(h, 4))
            rtm &= _sb(small, j) & _sb(black, j) & (f(o, j) < f(h, 4)) & (f(c, j) > f(l, 4))
        out["falling_three_methods_bear"] = ftm & long_ & black & (c < f(c, 4))
        out["rising_three_methods_bull"] = rtm & long_ & white & (c > f(c, 4))
        not_doji_or_shadows = ~doji_body | (has_up & has_dn)
        out["tweezer_top_bear"] = (_sb(up, 1) & not_doji_or_shadows & (np.abs(h - f(h, 1)) <= body_avg * 0.05)
                                   & _sb(white, 1) & black & _sb(long_, 1))
        out["tweezer_bottom_bull"] = (_sb(down, 1) & not_doji_or_shadows & (np.abs(l - f(l, 1)) <= body_avg * 0.05)
                                      & _sb(black, 1) & white & _sb(long_, 1))
        out["dark_cloud_cover_bear"] = (_sb(up, 1) & _sb(white, 1) & _sb(long_, 1) & black & (o >= f(h, 1))
                                        & (c < f(body_mid, 1)) & (c > f(o, 1)))
        out["downside_tasuki_gap_bear"] = (_sb(long_, 2) & _sb(small, 1) & down & _sb(black, 2)
                                           & (f(body_hi, 1) < f(body_lo, 2)) & _sb(black, 1) & white
                                           & (body_hi <= f(body_lo, 2)) & (body_hi >= f(body_hi, 1)))
        out["upside_tasuki_gap_bull"] = (_sb(long_, 2) & _sb(small, 1) & up & _sb(white, 2)
                                         & (f(body_lo, 1) > f(body_hi, 2)) & _sb(white, 1) & black
                                         & (body_lo >= f(body_hi, 2)) & (body_lo <= f(body_lo, 1)))
        out["evening_doji_star_bear"] = (_sb(long_, 2) & _sb(doji_body, 1) & long_ & up & _sb(white, 2)
                                         & (f(body_lo, 1) > f(body_hi, 2)) & black & (body_lo <= f(body_mid, 2))
                                         & (body_lo > f(body_lo, 2)) & (f(body_lo, 1) > body_hi))
        out["doji_star_bear"] = up & _sb(white, 1) & _sb(long_, 1) & doji_body & (body_lo > f(body_hi, 1))
        out["doji_star_bull"] = down & _sb(black, 1) & _sb(long_, 1) & doji_body & (body_hi < f(body_lo, 1))
        out["morning_doji_star_bull"] = (_sb(long_, 2) & _sb(doji_body, 1) & long_ & down & _sb(black, 2)
                                         & (f(body_hi, 1) < f(body_lo, 2)) & white & (body_hi >= f(body_mid, 2))
                                         & (body_hi < f(body_hi, 2)) & (f(body_hi, 1) < body_lo))
        out["piercing_bull"] = (_sb(down, 1) & _sb(black, 1) & _sb(long_, 1) & white & (o <= f(l, 1))
                                & (c > f(body_mid, 1)) & (c < f(o, 1)))
        hammer_shape = small & (body > 0) & (body_lo > hl2) & (dn_sh >= factor * body) & ~has_up
        star_shape = small & (body > 0) & (body_hi < hl2) & (up_sh >= factor * body) & ~has_dn
        out["hammer_bull"] = hammer_shape & down
        out["hanging_man_bear"] = hammer_shape & up
        out["shooting_star_bear"] = star_shape & up
        out["inverted_hammer_bull"] = star_shape & down
        star3 = _sb(long_, 2) & _sb(small, 1) & long_
        out["morning_star_bull"] = (star3 & down & _sb(black, 2) & (f(body_hi, 1) < f(body_lo, 2)) & white
                                    & (body_hi >= f(body_mid, 2)) & (body_hi < f(body_hi, 2))
                                    & (f(body_hi, 1) < body_lo))
        out["evening_star_bear"] = (star3 & up & _sb(white, 2) & (f(body_lo, 1) > f(body_hi, 2)) & black
                                    & (body_lo <= f(body_mid, 2)) & (body_lo > f(body_lo, 2))
                                    & (f(body_lo, 1) > body_hi))
        maru = long_ & (up_sh <= 5.0 / 100 * body) & (dn_sh <= 5.0 / 100 * body)
        out["marubozu_white_bull"] = white & maru
        out["marubozu_black_bear"] = black & maru
        dragonfly = doji_body & (up_sh <= body)
        gravestone = doji_body & (dn_sh <= body)
        out["doji"] = doji_c & ~dragonfly & ~gravestone
        out["gravestone_doji_bear"] = gravestone
        out["dragonfly_doji_bull"] = dragonfly
        inside_body = (h <= f(body_hi, 1)) & (l >= f(body_lo, 1))
        out["harami_cross_bull"] = _sb(long_, 1) & _sb(black, 1) & _sb(down, 1) & doji_body & inside_body
        out["harami_cross_bear"] = _sb(long_, 1) & _sb(white, 1) & _sb(up, 1) & doji_body & inside_body
        out["harami_bull"] = _sb(long_, 1) & _sb(black, 1) & _sb(down, 1) & white & small & inside_body
        out["harami_bear"] = _sb(long_, 1) & _sb(white, 1) & _sb(up, 1) & black & small & inside_body
        out["long_lower_shadow_bull"] = dn_sh > rng / 100 * 75.0
        out["long_upper_shadow_bear"] = up_sh > rng / 100 * 75.0
        spin = (dn_sh >= rng / 100 * 34.0) & (up_sh >= rng / 100 * 34.0) & ~doji_body
        out["spinning_top_white"] = spin & white
        out["spinning_top_black"] = spin & black
        long3 = long_ & _sb(long_, 1) & _sb(long_, 2)
        no_up = rng * 5.0 / 100 > up_sh
        no_dn = rng * 5.0 / 100 > dn_sh
        out["three_white_soldiers_bull"] = (long3 & white & _sb(white, 1) & _sb(white, 2) & (c > f(c, 1))
                                            & (f(c, 1) > f(c, 2)) & (o < f(c, 1)) & (o > f(o, 1))
                                            & (f(o, 1) < f(c, 2)) & (f(o, 1) > f(o, 2))
                                            & no_up & _sb(no_up, 1) & _sb(no_up, 2))
        out["three_black_crows_bear"] = (long3 & black & _sb(black, 1) & _sb(black, 2) & (c < f(c, 1))
                                         & (f(c, 1) < f(c, 2)) & (o > f(c, 1)) & (o < f(o, 1))
                                         & (f(o, 1) > f(c, 2)) & (f(o, 1) < f(o, 2))
                                         & no_dn & _sb(no_dn, 1) & _sb(no_dn, 2))
        out["engulfing_bull"] = (down & white & long_ & _sb(black, 1) & _sb(small, 1) & (c >= f(o, 1))
                                 & (o <= f(c, 1)) & ((c > f(o, 1)) | (o < f(c, 1))))
        out["engulfing_bear"] = (up & black & long_ & _sb(white, 1) & _sb(small, 1) & (c <= f(o, 1))
                                 & (o >= f(c, 1)) & ((c < f(o, 1)) | (o > f(c, 1))))
        out["abandoned_baby_bull"] = (_sb(down, 2) & _sb(black, 2) & _sb(doji_body, 1) & (f(l, 2) > f(h, 1))
                                      & white & (f(h, 1) < l))
        out["abandoned_baby_bear"] = (_sb(up, 2) & _sb(white, 2) & _sb(doji_body, 1) & (f(h, 2) < f(l, 1))
                                      & black & (f(l, 1) > h))
        three_doji = _sb(doji_c, 2) & _sb(doji_c, 1) & doji_c
        gap_up = f(body_hi, 1) < body_lo
        gap_dn = f(body_lo, 1) > body_hi
        out["tri_star_bull"] = three_doji & _sb(down, 2) & _sb(gap_dn, 1) & gap_up
        out["tri_star_bear"] = three_doji & _sb(up, 2) & _sb(gap_up, 1) & gap_dn
        maru_w = maru & white
        maru_b = maru & black
        out["kicking_bull"] = _sb(maru_b, 1) & maru_w & (f(h, 1) < l)
        out["kicking_bear"] = _sb(maru_w, 1) & maru_b & (f(l, 1) > h)
        out["inside_bar"] = (h < f(h, 1)) & (l > f(l, 1))
        out["pin_bar_bull"] = (rng > 0) & (dn_sh >= pin_ratio * rng)
        out["pin_bar_bear"] = (rng > 0) & (up_sh >= pin_ratio * rng)
    return tuple(out[name] for name in _CANDLE_OUTPUTS)


# ---------------------------------------------------------------------------
# Zig Zag (TradingView built-in, TradingView/ZigZag/9), confirmed pivots only
# ---------------------------------------------------------------------------

@njit(cache=True)
def _zz_find(x, i, c, d, is_high):
    """ZigZag library ``findPivotPoint``: returns (found, price)."""
    p = x[i - d, c]
    if np.isnan(p):
        p = 0.0  # nz(source[depth])
    if 2 * d > i:
        return False, p
    for j in range(d):  # newer bars: may tie
        v = x[i - j, c]
        if (is_high and v > p) or ((not is_high) and v < p):
            return False, p
    for j in range(d + 1, 2 * d + 1):  # older bars: must be strictly beyond
        v = x[i - j, c]
        if (is_high and v >= p) or ((not is_high) and v <= p):
            return False, p
    return True, p


@njit(cache=True)
def _zigzag_nb(high, low, dev_thr, d, one_bar):
    shape = high.shape
    direction = np.full(shape, NAN)
    piv_price = np.full(shape, NAN)
    piv_bar = np.full(shape, NAN)
    prev_price = np.full(shape, NAN)
    prev_bar = np.full(shape, NAN)
    new_piv = np.zeros(shape, dtype=np.bool_)
    updated = np.zeros(shape, dtype=np.bool_)
    sw_hi = np.full(shape, NAN)
    sw_hi_bar = np.full(shape, NAN)
    sw_lo = np.full(shape, NAN)
    sw_lo_bar = np.full(shape, NAN)
    for c in range(shape[1]):
        count = 0
        last_hi = False
        last_p = NAN
        last_b = -1
        start_p = NAN
        start_b = -1
        for i in range(shape[0]):
            reg_high = False
            for side in range(2):
                is_high = side == 0
                if (not is_high) and not (one_bar or not reg_high):
                    continue
                found, p = _zz_find(high if is_high else low, i, c, d, is_high)
                if not found:
                    continue
                b = i - d
                res = False
                if count == 0:
                    count = 1
                    last_hi, last_p, last_b = is_high, p, b
                    start_p, start_b = p, b
                    new_piv[i, c] = True
                    res = True
                elif last_hi == is_high:
                    m = 1.0 if last_hi else -1.0
                    if p * m > last_p * m:
                        if count == 1:
                            start_p, start_b = p, b
                        last_p, last_b = p, b
                        updated[i, c] = True
                        res = True
                else:
                    dev = 100 * (p - last_p) / abs(last_p) if last_p != 0 else NAN
                    if ((not last_hi) and dev >= dev_thr) or (last_hi and dev <= -dev_thr):
                        if last_hi:
                            sw_hi[i, c] = last_p
                            sw_hi_bar[i, c] = last_b
                        else:
                            sw_lo[i, c] = last_p
                            sw_lo_bar[i, c] = last_b
                        start_p, start_b = last_p, last_b
                        last_hi, last_p, last_b = is_high, p, b
                        count += 1
                        new_piv[i, c] = True
                        res = True
                if is_high:
                    reg_high = res
            if count > 0:
                direction[i, c] = 1.0 if last_hi else -1.0
                piv_price[i, c] = last_p
                piv_bar[i, c] = last_b
                if count > 1:
                    prev_price[i, c] = start_p
                    prev_bar[i, c] = start_b
    return (direction, piv_price, piv_bar, prev_price, prev_bar, new_piv, updated,
            sw_hi, sw_hi_bar, sw_lo, sw_lo_bar)


@indicator("ZIGZAG", ["high", "low"],
           ["direction", "pivot_price", "pivot_bar", "prev_price", "prev_bar", "new_pivot",
            "updated", "swing_high", "swing_high_bar", "swing_low", "swing_low_bar"])
def zigzag(high, low, deviation=5.0, depth=10, allow_zigzag_on_one_bar=True):
    """TradingView's "Zigzag" (``STD;Zig_Zag``, library TradingView/ZigZag/9),
    without repainting: each bar shows only what the library knows on that
    bar's close.

    Port of ``ZigZag.update()`` with projections off. The built-in projects a
    temporary pivot on the last bar only, and that projection repaints, so it
    is left out. With d = max(2, floor(depth / 2)), a pivot candidate is the
    high (low) ``d`` bars back. It must be strictly beyond the ``d`` older
    bars and at least equal to the ``d`` newer ones. A candidate in the same
    direction as the last pivot moves that pivot if it goes further
    (``updated``). An opposite candidate starts a new leg only if it is at
    least ``deviation`` % away from the last pivot (``new_pivot``). The first
    candidate is always taken.

    Outputs, as known on each bar:

    * ``direction``: +1 if the last pivot is a high (last leg up), -1 if it is
      a low. ``pivot_price`` / ``pivot_bar`` give that pivot (bar = row
      number). It can still move further.
    * ``prev_price`` / ``prev_bar``: the pivot before it, which is final.
    * ``swing_high`` / ``swing_low`` (with ``*_bar``): a swing price emitted
      once, on the bar where it becomes final, i.e. when the opposite pivot
      is registered. NaN on other bars.

    Delays: a pivot is detected exactly ``d`` bars after its bar (5 with the
    default depth 10), and only if it passes the deviation test. A swing is
    final when the next opposite pivot is detected, at least ``d`` bars
    after that later pivot's bar. TradingView's finished historical drawing
    joins these same pivots. Only its last leg differs.
    """
    d = max(2, int(depth) // 2)
    return _zigzag_nb(high, low, float(deviation), d, bool(allow_zigzag_on_one_bar))


# ---------------------------------------------------------------------------
# Linear regression channel (TradingView built-in)
# ---------------------------------------------------------------------------

@njit(cache=True)
def _linreg_channel_nb(src, high, low, n, use_up, up_mult, use_dn, dn_mult):
    shape = src.shape
    mid = np.full(shape, NAN)
    upper = np.full(shape, NAN)
    lower = np.full(shape, NAN)
    pr = np.full(shape, NAN)
    slope_out = np.full(shape, NAN)
    sd_out = np.full(shape, NAN)
    if n <= 1:
        return upper, mid, lower, pr, slope_out, sd_out
    for c in range(shape[1]):
        for b in range(n - 1, shape[0]):
            # calcSlope: x = 1 for the current bar, n for the oldest
            sum_x = 0.0
            sum_y = 0.0
            sum_xx = 0.0
            sum_xy = 0.0
            for i in range(n):
                val = src[b - i, c]
                per = i + 1.0
                sum_x += per
                sum_y += val
                sum_xx += per * per
                sum_xy += val * per
            s = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
            a = sum_y / n
            icpt = a - s * sum_x / n + s
            # calcDev
            up_dev = 0.0
            dn_dev = 0.0
            acc = 0.0
            dsxx = 0.0
            dsyy = 0.0
            dsxy = 0.0
            periods = n - 1
            day = icpt + s * periods / 2
            val = icpt
            for j in range(periods + 1):
                price = high[b - j, c] - val
                if price > up_dev:
                    up_dev = price
                price = val - low[b - j, c]
                if price > dn_dev:
                    dn_dev = price
                price = src[b - j, c]
                dxt = price - a
                dyt = val - day
                price -= val
                acc += price * price
                dsxx += dxt * dxt
                dsyy += dyt * dyt
                dsxy += dxt * dyt
                val += s
            sd = np.sqrt(acc / (1 if periods == 0 else periods))
            r = 0.0 if (dsxx == 0 or dsyy == 0) else dsxy / np.sqrt(dsxx * dsyy)
            mid[b, c] = icpt
            upper[b, c] = icpt + (up_mult * sd if use_up else up_dev)
            lower[b, c] = icpt + (-dn_mult * sd if use_dn else -dn_dev)
            pr[b, c] = r
            slope_out[b, c] = -s
            sd_out[b, c] = sd
    return upper, mid, lower, pr, slope_out, sd_out


@indicator("LINREG_CHANNEL", ["high", "low", "close"],
           ["upper", "mid", "lower", "pearson_r", "slope", "stdev"])
def linreg_channel(high, low, close, length=100, upper_mult=2.0, lower_mult=2.0,
                   use_upper_dev=True, use_lower_dev=True):
    """TradingView's "Linear regression channel" (``STD;Linear_Regression``),
    evaluated on every bar as if it were the chart's last bar.

    The built-in computes only on ``barstate.islast`` and redraws. Here each
    bar gets the value of the channel's right end that TradingView would
    show if that bar were the last, so nothing repaints.

    * ``mid``: the regression line at the current bar (``endPrice``).
    * ``upper`` / ``lower``: ``mid +/- mult * stdev``. ``stdev`` is the RMS of
      the residuals divided by ``length - 1``. With ``use_*_dev=False`` the
      built-in instead uses the largest ``high`` above (``low`` below) the line.
    * ``pearson_r``: the built-in's Pearson's R label. It is the correlation of
      price with the fitted line, so it is >= 0 and 0 for a flat line.
    * ``slope``: change of the line per bar, forward in time (-1 x the
      script's ``slope``, which runs backwards from the current bar).

    ``close`` is the "Source" input. The line at the oldest bar of the window
    is ``mid - slope * (length - 1)``.
    """
    return _linreg_channel_nb(close, high, low, int(length), bool(use_upper_dev), float(upper_mult),
                              bool(use_lower_dev), float(lower_mult))


# ---------------------------------------------------------------------------
# Higher-timeframe alignment (request.security without repainting)
# ---------------------------------------------------------------------------

_ANCHORED = {"W": "W-MON", "1W": "W-MON", "M": "MS", "1M": "MS", "ME": "MS", "Q": "QS", "QE": "QS",
             "Y": "YS", "A": "YS", "YE": "YS"}


def _norm_rule(rule):
    r = str(rule).strip()
    return _ANCHORED.get(r.upper(), r)


def _htf_close_times(index, rule):
    off = pd.tseries.frequencies.to_offset(_norm_rule(rule))
    return index + off


def _ns(idx):
    """int64 nanoseconds; pandas 3 indexes may be in us, so never mix ``asi8`` units."""
    return pd.DatetimeIndex(idx).as_unit("ns").asi8


def resample_ohlcv(df, rule):
    """Build higher-timeframe OHLCV bars from chart bars, as TradingView does.

    Each HTF bar is labelled with its **open** time. Bins are closed on the
    left: [open, open + rule). Weeks start on Monday ("W" -> "W-MON") and
    months, quarters and years at their first day ("M" -> "MS"), like
    TradingView's bars. Intraday and daily bins are anchored at midnight of
    the index's timezone. Empty periods (no chart bars) are dropped.
    Columns used: open, high, low, close and volume if present. A
    ``close_time`` column is added (bin end), which ``htf`` uses.
    """
    rule = _norm_rule(rule)
    agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
    if "volume" in df.columns:
        agg["volume"] = "sum"
    out = df[list(agg)].resample(rule, closed="left", label="left").agg(agg)
    out = out[out["close"].notna()]
    out["close_time"] = _htf_close_times(out.index, rule)
    return out


def htf(series_on_htf_bars, chart_index, mode="lookahead_off", rule=None, chart_freq=None, gaps=False):
    """Show a series computed on HTF bars on the chart's bars, the way
    ``request.security`` does on historical bars, without repainting.

    ``series_on_htf_bars`` is a Series/DataFrame indexed by HTF bar open time
    (e.g. ``ti.sma(resample_ohlcv(df, "D").close, 20)``). ``chart_index`` is
    the chart's DatetimeIndex of bar open times. A chart bar belongs to the
    last HTF bar that opened at or before it.

    * ``mode="lookahead_off"``: ``request.security(sym, tf, expr)``. The Pine
      manual says it "has a new historical value at the end of each HTF
      period". HTF bar k's value appears on the chart bar whose close time
      reaches k's close time (the last chart bar of the period, e.g. the
      23:00 bar of an hourly chart for a daily bar). Earlier bars of the
      period show bar k-1. If that last chart bar is missing, the value
      appears on the next chart bar, the first after the HTF close. On
      realtime bars TradingView would show the developing value instead
      (it repaints), so this matches its historical bars only.
    * ``mode="lookahead_on_offset1"``: ``request.security(sym, tf, expr[1],
      lookahead = barmerge.lookahead_on)``, which the manual calls "the only
      recommended method to avoid repainting". HTF bar k-1's value is shown
      from the first chart bar of HTF bar k through its last bar. That is one
      chart bar after "lookahead_off" when the bars align, and the same on
      historical and realtime bars.

    HTF close times come from a ``close_time`` column (``resample_ohlcv``
    adds one), else from ``rule``, else from the next HTF bar's open time
    (the last bar adds the median spacing). Chart bar close = open +
    ``chart_freq`` (default: the smallest spacing in ``chart_index``).
    ``gaps=True`` is ``barmerge.gaps_on``: NaN except on the chart bar where
    a new HTF value arrives. Chart bars before the first HTF bar get NaN.
    """
    if mode not in ("lookahead_off", "lookahead_on_offset1"):
        raise ValueError("mode must be 'lookahead_off' or 'lookahead_on_offset1'")
    s = series_on_htf_bars
    close_t = None
    if isinstance(s, pd.DataFrame) and "close_time" in s.columns:
        close_t = pd.DatetimeIndex(s["close_time"])
        s = s.drop(columns="close_time")
    hidx = pd.DatetimeIndex(s.index)
    if close_t is None:
        if rule is not None:
            close_t = _htf_close_times(hidx, rule)
        else:
            nxt = hidx[1:].append(hidx[-1:] + (pd.Series(hidx).diff().median()
                                               if len(hidx) > 1 else pd.Timedelta(0)))
            close_t = pd.DatetimeIndex(nxt)
    cidx = pd.DatetimeIndex(chart_index)
    c_ns, h_ns, hc_ns = _ns(cidx), _ns(hidx), _ns(close_t)
    if chart_freq is None:
        d = np.diff(c_ns)
        step = int(d[d > 0].min()) if (d > 0).any() else 0
    else:
        step = pd.Timedelta(pd.tseries.frequencies.to_offset(chart_freq)).value
    cclose = c_ns + step

    kk = np.searchsorted(h_ns, c_ns, side="right") - 1  # HTF bar containing the chart bar
    if mode == "lookahead_off":
        done = np.zeros(len(cidx), dtype=bool)
        ok = kk >= 0
        done[ok] = cclose[ok] >= hc_ns[kk[ok]]
        src = np.where(done, kk, kk - 1)
    else:
        src = kk - 1
    vals = s.to_numpy(dtype=float)
    if vals.ndim == 1:
        vals = vals.reshape(-1, 1)
    out = np.full((len(cidx), vals.shape[1]), NAN)
    m = src >= 0
    out[m] = vals[src[m]]
    if gaps:
        prev = np.r_[-1, src[:-1]]
        out[src == prev] = NAN
    if isinstance(s, pd.DataFrame):
        return pd.DataFrame(out, index=cidx, columns=s.columns)
    return pd.Series(out[:, 0], index=cidx, name=getattr(s, "name", None))


# Keep these out of tv_indicators' registry so the main library is unchanged.
EXTRA_TV = {name: REGISTRY.pop(name) for name in list(REGISTRY) if name not in _BEFORE}

__all__ = sorted([fn.__name__ for fn in EXTRA_TV.values()] + ["htf", "resample_ohlcv"])
