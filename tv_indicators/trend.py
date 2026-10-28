"""Trend-strength and trend-following indicators."""

import numpy as np

from . import kernels as k
from ._core import change_2d, indicator, safe_div, shift_2d


@indicator("DMI", ["high", "low", "close"], ["plus_di", "minus_di", "adx"])
def dmi(high, low, close, di_length=14, adx_smoothing=14):
    """Directional Movement Index + ADX (TradingView built-in "DMI", 14 / 14)."""
    n, s = int(di_length), int(adx_smoothing)
    up = change_2d(high)
    down = -change_2d(low)
    with np.errstate(invalid="ignore"):
        plus_dm = np.where(np.isnan(up), np.nan, np.where((up > down) & (up > 0), up, 0.0))
        minus_dm = np.where(np.isnan(down), np.nan, np.where((down > up) & (down > 0), down, 0.0))
    trur = k.rma_nb(k.tr_nb(high, low, close, False), n)
    plus = k.fixnan_nb(safe_div(100 * k.rma_nb(plus_dm, n), trur))
    minus = k.fixnan_nb(safe_div(100 * k.rma_nb(minus_dm, n), trur))
    total = plus + minus
    adx_ = 100 * k.rma_nb(np.abs(plus - minus) / np.where(total == 0, 1.0, total), s)
    return plus, minus, adx_


@indicator("ADX", ["high", "low", "close"], ["adx"])
def adx(high, low, close, di_length=14, adx_smoothing=14):
    """ADX line only (same numbers as :func:`dmi`)."""
    return dmi.core(high, low, close, di_length, adx_smoothing)[2]


@indicator("AROON", ["high", "low"], ["up", "down", "oscillator"])
def aroon(high, low, length=14):
    """Aroon (TradingView built-in, 14). Uses ``length + 1`` bars, like TV."""
    n = int(length)
    up = 100 * (k.highestbars_nb(high, n + 1) + n) / n
    dn = 100 * (k.lowestbars_nb(low, n + 1) + n) / n
    return up, dn, up - dn


@indicator("ICHIMOKU", ["high", "low", "close"],
           ["tenkan", "kijun", "senkou_a", "senkou_b", "lead_a", "lead_b", "chikou"])
def ichimoku(high, low, close, conversion=9, base=26, span_b=52, displacement=26):
    """Ichimoku Cloud (TradingView built-in: 9 / 26 / 52 / 26).

    * ``senkou_a`` / ``senkou_b``: the cloud as drawn *under the current bar*
      (lead lines shifted forward by ``displacement - 1``, as TV plots them).
      Use these for "price above cloud" rules - no look-ahead.
    * ``lead_a`` / ``lead_b``: the unshifted lead lines computed on this bar
      (the cloud TV draws ``displacement - 1`` bars into the future).
    * ``chikou``: close shifted *back*, i.e. ``close[t + displacement - 1]``.
      It uses future data; never feed it to signals.
    """
    def mid(n):
        return (k.lowest_nb(low, int(n)) + k.highest_nb(high, int(n))) / 2

    tenkan = mid(conversion)
    kijun = mid(base)
    lead_a = (tenkan + kijun) / 2
    lead_b = mid(span_b)
    off = int(displacement) - 1
    return (tenkan, kijun, shift_2d(lead_a, off), shift_2d(lead_b, off),
            lead_a, lead_b, shift_2d(close, -off))


@indicator("ADXR", ["high", "low", "close"], ["adxr"])
def adxr(high, low, close, length=14):
    """Average Directional Movement Rating: (ADX + ADX[length-1]) / 2 (TA-Lib)."""
    a = dmi.core(high, low, close, length, length)[2]
    return (a + shift_2d(a, int(length) - 1)) / 2
