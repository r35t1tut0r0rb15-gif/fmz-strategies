"""Volume indicators."""

import numpy as np
import pandas as pd

from . import kernels as k
from ._core import change_2d, f2d, indicator, safe_div, shift_2d


def _clv_volume(high, low, close, volume):
    rng = high - low
    with np.errstate(divide="ignore", invalid="ignore"):
        mf = (2 * close - low - high) / rng * volume
    zero = ((close == high) & (close == low)) | (rng == 0)
    return np.where(zero, 0.0, mf)


@indicator("OBV", ["close", "volume"], ["obv"])
def obv(close, volume):
    """On Balance Volume = ta.cum(sign(change(close)) * volume). Starts at bar 1."""
    return k.cum_nb(np.sign(change_2d(close)) * volume)


@indicator("AD", ["high", "low", "close", "volume"], ["ad"])
def accdist(high, low, close, volume):
    """Accumulation/Distribution = ``ta.accdist``."""
    return k.cum_nb(_clv_volume(high, low, close, volume))


@indicator("CMF", ["high", "low", "close", "volume"], ["cmf"])
def cmf(high, low, close, volume, length=20):
    """Chaikin Money Flow (TradingView built-in, 20)."""
    n = int(length)
    return safe_div(k.sum_nb(_clv_volume(high, low, close, volume), n), k.sum_nb(volume, n))


@indicator("CHAIKIN_OSC", ["high", "low", "close", "volume"], ["chaikin_osc"])
def chaikin_osc(high, low, close, volume, fast=3, slow=10):
    """Chaikin Oscillator = ema(accdist, 3) - ema(accdist, 10)."""
    ad = k.cum_nb(_clv_volume(high, low, close, volume))
    return k.ema_nb(ad, int(fast)) - k.ema_nb(ad, int(slow))


@indicator("PVT", ["close", "volume"], ["pvt"])
def pvt(close, volume):
    """Price Volume Trend = ta.cum(change(close) / close[1] * volume)."""
    return k.cum_nb(safe_div(change_2d(close), shift_2d(close, 1)) * volume)


@indicator("EFI", ["close", "volume"], ["efi"])
def efi(close, volume, length=13):
    """Elder Force Index = ema(change(close) * volume, 13)."""
    return k.ema_nb(change_2d(close) * volume, int(length))


@indicator("VWAP_SESSION", ["high", "low", "close", "volume", "session"],
           ["vwap", "upper", "lower"])
def vwap_session(high, low, close, volume, session, band_mult=1.0):
    """VWAP on ``hlc3`` that resets whenever ``session`` changes value.

    Use :func:`vwap` with a DatetimeIndex unless you need custom anchors.
    Bands are vwap +/- band_mult * volume-weighted stdev, as in TV's VWAP.
    """
    src = (high + low + close) / 3
    vw, sd = k.vwap_nb(src, volume, session)
    return vw, vw + band_mult * sd, vw - band_mult * sd


_ANCHORS = {"D": "D", "W": "W-SUN", "M": "M", "Q": "Q", "Y": "Y"}


def session_ids(index, anchor="D"):
    """Integer period ids for a DatetimeIndex: D, W (Mon-Sun), M, Q or Y.

    Periods follow the index's own timezone - localize the index to the
    exchange timezone first if you want TradingView's session boundaries.
    """
    if not isinstance(index, pd.DatetimeIndex):
        raise TypeError("vwap() needs a DatetimeIndex; use vwap_session() otherwise")
    try:
        freq = _ANCHORS[anchor.upper()]
    except KeyError:
        raise ValueError(f"anchor must be one of {list(_ANCHORS)}")
    idx = index.tz_localize(None) if index.tz is not None else index
    return pd.factorize(idx.to_period(freq))[0].astype(float)


def vwap(high, low, close, volume, anchor="D", band_mult=1.0):
    """Session VWAP (TradingView built-in "VWAP", anchor Session/Week/Month...).

    Inputs must be pandas objects with a DatetimeIndex.
    """
    sess = session_ids(close.index, anchor)
    width = f2d(close).shape[1]
    sess = np.repeat(sess.reshape(-1, 1), width, axis=1)
    if isinstance(close, pd.DataFrame):
        sess = pd.DataFrame(sess, index=close.index, columns=close.columns)
    else:
        sess = pd.Series(sess[:, 0], index=close.index)
    return vwap_session(high, low, close, volume, sess, band_mult)
