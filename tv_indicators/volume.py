"""Volume indicators."""

import numpy as np
import pandas as pd
from numba import njit

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


@indicator("EOM", ["high", "low", "volume"], ["eom"])
def ease_of_movement(high, low, volume, length=14, divisor=10000):
    """Ease of Movement (TradingView built-in, 14, divisor 10000)."""
    hl2 = (high + low) / 2
    return k.sma_nb(safe_div(divisor * change_2d(hl2) * (high - low), volume), int(length))


@njit(cache=True)
def _volume_index_nb(close, volume, negative, start):
    out = np.full(close.shape, np.nan)
    for c in range(close.shape[1]):
        v = start
        out[0, c] = v
        for i in range(1, close.shape[0]):
            dv = volume[i, c] - volume[i - 1, c]
            if (dv < 0 if negative else dv > 0) and close[i - 1, c] != 0:
                v = v * close[i, c] / close[i - 1, c]
            out[i, c] = v
    return out


@indicator("NVI", ["close", "volume"], ["nvi", "signal"])
def nvi(close, volume, start=1000.0, signal_length=255):
    """Negative Volume Index (changes only on bars where volume falls) + EMA 255."""
    v = _volume_index_nb(close, volume, True, float(start))
    return v, k.ema_nb(v, int(signal_length))


@indicator("PVI", ["close", "volume"], ["pvi", "signal"])
def pvi(close, volume, start=1000.0, signal_length=255):
    """Positive Volume Index (changes only on bars where volume rises) + EMA 255."""
    v = _volume_index_nb(close, volume, False, float(start))
    return v, k.ema_nb(v, int(signal_length))


@indicator("KLINGER", ["high", "low", "close", "volume"], ["kvo", "signal"])
def klinger(high, low, close, volume, fast=34, slow=55, signal=13):
    """Klinger Oscillator (TradingView built-in version: signed volume EMAs)."""
    ch = change_2d((high + low + close) / 3)
    with np.errstate(invalid="ignore"):
        sv = np.where(np.isnan(ch), np.nan, np.where(ch >= 0, volume, -volume))
    kvo = k.ema_nb(sv, int(fast)) - k.ema_nb(sv, int(slow))
    return kvo, k.ema_nb(kvo, int(signal))


@indicator("NET_VOLUME", ["close", "volume"], ["net_volume"])
def net_volume(close, volume):
    """Net Volume (TradingView built-in): +volume on up closes, -volume on down."""
    return np.sign(change_2d(close)) * volume


@indicator("WILLIAMS_AD", ["high", "low", "close"], ["wad"])
def williams_ad(high, low, close):
    """Williams Accumulation/Distribution (cumulative, no volume)."""
    pc = shift_2d(close, 1)
    trh = np.fmax(high, pc)
    trl = np.fmin(low, pc)
    with np.errstate(invalid="ignore"):
        ad = np.where(close > pc, close - trl, np.where(close < pc, close - trh, 0.0))
    ad[np.isnan(pc)] = np.nan
    return k.cum_nb(ad)


@indicator("RVOL", ["volume"], ["rvol"])
def relative_volume(volume, length=20):
    """Relative Volume: volume / sma(volume, length)."""
    return safe_div(volume, k.sma_nb(volume, int(length)))


@indicator("VFI", ["high", "low", "close", "volume"], ["vfi", "signal", "hist"])
def vfi(high, low, close, volume, length=130, coef=0.2, vcoef=2.5, signal_length=5, smooth=False):
    """Volume Flow Indicator [LazyBear]."""
    n = int(length)
    tp = (high + low + close) / 3
    with np.errstate(divide="ignore", invalid="ignore"):
        inter = np.log(tp) - np.log(shift_2d(tp, 1))
    cutoff = coef * k.stdev_nb(inter, 30) * close
    vave = shift_2d(k.sma_nb(volume, n), 1)
    vc = np.where(volume < vave * vcoef, volume, vave * vcoef)
    mf = change_2d(tp)
    with np.errstate(invalid="ignore"):
        vcp = np.where(mf > cutoff, vc, np.where(mf < -cutoff, -vc, 0.0))
    v = safe_div(k.sum_nb(vcp, n), vave)
    if smooth:
        v = k.sma_nb(v, 3)
    s = k.ema_nb(v, int(signal_length))
    return v, s, v - s


@indicator("VZO", ["close", "volume"], ["vzo"])
def volume_zone_oscillator(close, volume, length=14):
    """Volume Zone Oscillator (Khalil & Steckler): 100*ema(signed vol)/ema(vol)."""
    n = int(length)
    return safe_div(k.ema_nb(np.sign(change_2d(close)) * volume, n), k.ema_nb(volume, n)) * 100


@indicator("ROLLING_VWAP", ["high", "low", "close", "volume"], ["vwap"])
def rolling_vwap(high, low, close, volume, length=20):
    """VWAP of hlc3 over the last ``length`` bars (bar-count rolling window)."""
    tp = (high + low + close) / 3
    n = int(length)
    return safe_div(k.sum_nb(tp * volume, n), k.sum_nb(volume, n))
