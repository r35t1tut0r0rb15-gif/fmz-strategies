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


@indicator("FRACTALS", ["high", "low"], ["up", "down", "up_level", "down_level"])
def fractals(high, low, periods=2):
    """Williams Fractals, reported when *confirmed* (``periods`` bars later).

    A fractal on bar t-n is flagged on bar t, so there is no look-ahead.
    ``up_level``/``down_level`` hold the price of the most recent confirmed
    fractal. Uses strict comparisons on both sides; TradingView's built-in
    also accepts some equal highs/lows to the right, so rare ties differ.
    """
    n = int(periods)
    ph, pl = shift_2d(high, n), shift_2d(low, n)
    up = np.ones(high.shape, dtype=bool)
    dn = np.ones(high.shape, dtype=bool)
    with np.errstate(invalid="ignore"):
        for j in range(1, n + 1):
            up &= (ph > shift_2d(high, n + j)) & (ph > shift_2d(high, n - j))
            dn &= (pl < shift_2d(low, n + j)) & (pl < shift_2d(low, n - j))
    up_level = k.fixnan_nb(np.where(up, ph, np.nan))
    down_level = k.fixnan_nb(np.where(dn, pl, np.nan))
    return up, dn, up_level, down_level


@indicator("BW_MFI", ["high", "low", "volume"], ["bw_mfi"])
def market_facilitation_index(high, low, volume):
    """Market Facilitation Index: (high - low) / volume."""
    return safe_div(high - low, volume)
