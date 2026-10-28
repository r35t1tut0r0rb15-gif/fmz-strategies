"""Moving averages and price sources."""

import numpy as np

from . import kernels as k
from ._core import hma_2d, indicator, ma_2d


# --- price sources ---------------------------------------------------------

@indicator("HL2", ["high", "low"], ["hl2"])
def hl2(high, low):
    """``hl2``."""
    return (high + low) / 2


@indicator("HLC3", ["high", "low", "close"], ["hlc3"])
def hlc3(high, low, close):
    """``hlc3`` (typical price)."""
    return (high + low + close) / 3


@indicator("OHLC4", ["open", "high", "low", "close"], ["ohlc4"])
def ohlc4(open, high, low, close):
    """``ohlc4``."""
    return (open + high + low + close) / 4


@indicator("HLCC4", ["high", "low", "close"], ["hlcc4"])
def hlcc4(high, low, close):
    """``hlcc4``."""
    return (high + low + 2 * close) / 4


# --- averages ----------------------------------------------------------------

@indicator("SMA", ["close"], ["sma"])
def sma(close, length=9):
    """``ta.sma``. TradingView "Moving Average Simple" default length 9."""
    return k.sma_nb(close, int(length))


@indicator("EMA", ["close"], ["ema"])
def ema(close, length=9):
    """``ta.ema``, SMA-seeded. TradingView "Moving Average Exponential" default 9."""
    return k.ema_nb(close, int(length))


@indicator("RMA", ["close"], ["rma"])
def rma(close, length=14):
    """``ta.rma`` (Wilder's smoothing, a.k.a. SMMA)."""
    return k.rma_nb(close, int(length))


@indicator("WMA", ["close"], ["wma"])
def wma(close, length=9):
    """``ta.wma``."""
    return k.wma_nb(close, int(length))


@indicator("VWMA", ["close", "volume"], ["vwma"])
def vwma(close, volume, length=20):
    """``ta.vwma`` = sma(close*volume) / sma(volume)."""
    return ma_2d(close, length, "vwma", volume)


@indicator("HMA", ["close"], ["hma"])
def hma(close, length=9):
    """``ta.hma``: wma(2*wma(x, n/2) - wma(x, n), round(sqrt(n)))."""
    return hma_2d(close, int(length))


@indicator("DEMA", ["close"], ["dema"])
def dema(close, length=9):
    """Double EMA: 2*e1 - ema(e1)."""
    return ma_2d(close, length, "dema")


@indicator("TEMA", ["close"], ["tema"])
def tema(close, length=9):
    """Triple EMA: 3*(e1 - e2) + e3."""
    return ma_2d(close, length, "tema")


@indicator("ALMA", ["close"], ["alma"])
def alma(close, length=9, offset=0.85, sigma=6.0, floor=False):
    """``ta.alma`` (Arnaud Legoux MA). TradingView defaults 9 / 0.85 / 6."""
    return k.alma_nb(close, int(length), float(offset), float(sigma), bool(floor))


@indicator("LSMA", ["close"], ["lsma"])
def lsma(close, length=25, offset=0):
    """Least Squares MA = ``ta.linreg(close, length, offset)``. TV default 25."""
    return k.linreg_nb(close, int(length), int(offset))


@indicator("MCGINLEY", ["close"], ["mcginley"])
def mcginley(close, length=14):
    """McGinley Dynamic (TradingView built-in), seeded with ``ta.ema``."""
    n = int(length)
    return k.mcginley_nb(close, k.ema_nb(close, n), float(n))


@indicator("KAMA", ["close"], ["kama"])
def kama(close, length=10, fast=2, slow=30):
    """Kaufman Adaptive MA (not a TV built-in; matches TA-Lib's KAMA)."""
    return k.kama_nb(close, int(length), float(fast), float(slow))


@indicator("MA", ["close", "volume"], ["ma"])
def ma(close, volume=np.nan, length=20, ma_type="sma"):
    """Any average by name: sma, ema, rma/smma, wma, vwma, hma, dema, tema, lsma.

    ``volume`` is only used by ``vwma`` and may be left out otherwise.
    """
    return ma_2d(close, length, ma_type, volume)
