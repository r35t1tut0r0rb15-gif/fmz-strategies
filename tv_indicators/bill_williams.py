"""Bill Williams' indicators (AO and AC live in the oscillator modules)."""

import numpy as np

from . import kernels as k
from ._core import indicator, safe_div, shift_2d


def _alligator(high, low, jaw_length, jaw_offset, teeth_length, teeth_offset, lips_length, lips_offset):
    src = (high + low) / 2
    jaw = shift_2d(k.rma_nb(src, int(jaw_length)), int(jaw_offset))
    teeth = shift_2d(k.rma_nb(src, int(teeth_length)), int(teeth_offset))
    lips = shift_2d(k.rma_nb(src, int(lips_length)), int(lips_offset))
    return jaw, teeth, lips


@indicator("ALLIGATOR", ["high", "low"], ["jaw", "teeth", "lips"])
def alligator(high, low, jaw_length=13, jaw_offset=8, teeth_length=8, teeth_offset=5,
              lips_length=5, lips_offset=3):
    """Williams Alligator (TradingView built-in): SMMA of hl2, shifted forward.

    The values are what TV draws *under the current bar* (computed
    ``offset`` bars ago), so they are safe to use in signals.
    """
    return _alligator(high, low, jaw_length, jaw_offset, teeth_length, teeth_offset, lips_length, lips_offset)


@indicator("GATOR", ["high", "low"], ["upper", "lower"])
def gator(high, low, jaw_length=13, jaw_offset=8, teeth_length=8, teeth_offset=5,
          lips_length=5, lips_offset=3):
    """Gator Oscillator: |jaw - teeth| above zero, -|teeth - lips| below."""
    jaw, teeth, lips = _alligator(high, low, jaw_length, jaw_offset, teeth_length, teeth_offset,
                                  lips_length, lips_offset)
    return np.abs(jaw - teeth), -np.abs(teeth - lips)


def _fractal_flags(x, n, sign):
    """TradingView's Williams Fractals test for bar ``n`` bars ago.

    ``sign=1`` for up fractals on highs, ``-1`` for down fractals on lows.
    Newer bars must be strictly lower (higher); up to 4 older bars may tie.
    """
    y = sign * x  # turn the low test into a high test
    c = shift_2d(y, n)

    def s(j):
        return shift_2d(y, j)

    with np.errstate(invalid="ignore"):
        down = np.ones(x.shape, dtype=bool)
        for i in range(1, n + 1):
            down &= s(n - i) < c
        any_up = np.zeros(x.shape, dtype=bool)
        for t in range(5):  # upflagUpFrontier0..4
            ties = np.ones(x.shape, dtype=bool)
            for j in range(1, t + 1):
                ties &= s(n + j) <= c
            flag = np.ones(x.shape, dtype=bool)
            for i in range(1, n + 1):
                flag &= ties & (s(n + i + t) < c)
            any_up |= flag
    return down & any_up


@indicator("FRACTALS", ["high", "low"], ["up", "down", "up_level", "down_level"])
def fractals(high, low, periods=2):
    """Williams Fractals (TradingView built-in), flagged when *confirmed*.

    A fractal on bar t-n is flagged on bar t (TV draws it ``n`` bars back),
    so there is no look-ahead. Same tie rules as TV: the ``n`` newer bars
    must be strictly lower/higher, and up to 4 older bars may be equal.
    ``up_level``/``down_level`` hold the price of the latest confirmed fractal.
    """
    n = int(periods)
    up = _fractal_flags(high, n, 1)
    dn = _fractal_flags(low, n, -1)
    up_level = k.fixnan_nb(np.where(up, shift_2d(high, n), np.nan))
    down_level = k.fixnan_nb(np.where(dn, shift_2d(low, n), np.nan))
    return up, dn, up_level, down_level


@indicator("BW_MFI", ["high", "low", "volume"], ["bw_mfi"])
def market_facilitation_index(high, low, volume):
    """Market Facilitation Index: (high - low) / volume."""
    return safe_div(high - low, volume)
