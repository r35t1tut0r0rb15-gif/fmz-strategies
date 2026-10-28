"""Bollinger Bands and everything built on them.

All definitions follow TradingView's built-in scripts unless the docstring
names a community script; those follow the published Pine source.
"""

import numpy as np
from numba import njit

from . import kernels as k
from ._core import indicator, ma_2d, safe_div


def _bb(close, length, mult, ma_type="sma", volume=None):
    """Basis/upper/lower as in TradingView's built-in Bollinger Bands.

    The basis can be any MA, but the deviation is always
    ``mult * ta.stdev(close, length)`` (population stdev).
    """
    n = int(length)
    basis = ma_2d(close, n, ma_type, volume)
    dev = mult * k.stdev_nb(close, n)
    return basis, basis + dev, basis - dev


@indicator("BBANDS", ["close", "volume"], ["basis", "upper", "lower", "bandwidth", "percent_b"])
def bbands(close, volume=np.nan, length=20, mult=2.0, ma_type="sma"):
    """Bollinger Bands (TradingView built-in).

    Defaults: length 20, StdDev 2, basis SMA. ``ma_type`` takes TradingView's
    options: "SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA" (needs ``volume``).
    ``bandwidth`` and ``percent_b`` are included for convenience and use the
    same definitions as :func:`bbw` and :func:`bb_percent_b`.
    """
    basis, upper, lower = _bb(close, length, mult, ma_type, volume)
    bw = safe_div(upper - lower, basis) * 100
    pb = safe_div(close - lower, upper - lower)
    return basis, upper, lower, bw, pb


@indicator("BB_PERCENT_B", ["close"], ["percent_b"])
def bb_percent_b(close, length=20, mult=2.0):
    """Bollinger Bands %B (TradingView built-in): (close-lower)/(upper-lower).

    Scale is 0..1 (not 0..100), like TradingView.
    """
    _, upper, lower = _bb(close, length, mult)
    return safe_div(close - lower, upper - lower)


@indicator("BBW", ["close"], ["bbw", "highest_expansion", "lowest_contraction", "squeeze"])
def bbw(close, length=20, mult=2.0, expansion_length=125, contraction_length=125):
    """Bollinger BandWidth (TradingView built-in): (upper-lower)/basis*100.

    ``highest_expansion`` / ``lowest_contraction`` are the built-in's
    reference lines (highest/lowest BBW over 125 bars). ``squeeze`` is
    Bollinger's own squeeze definition: BBW at its lowest in that window.
    """
    basis, upper, lower = _bb(close, length, mult)
    w = safe_div(upper - lower, basis) * 100
    hi = k.highest_nb(w, int(expansion_length))
    lo = k.lowest_nb(w, int(contraction_length))
    return w, hi, lo, w <= lo


@indicator("BBTREND", ["close"], ["bbtrend"])
def bbtrend(close, short_length=20, long_length=50, mult=2.0):
    """BBTrend by John Bollinger (TradingView built-in, 2024).

    (|shortLower - longLower| - |shortUpper - longUpper|) / shortMiddle * 100
    """
    sm, su, sl = _bb(close, short_length, mult)
    _, lu, ll = _bb(close, long_length, mult)
    return safe_div(np.abs(sl - ll) - np.abs(su - lu), sm) * 100


@indicator("BBWP", ["close", "volume"], ["bbwp", "bbwp_ma"])
def bbwp(close, volume=np.nan, length=13, lookback=252, ma_type="sma", ma_length=5):
    """Bollinger Band Width Percentile [The_Caretaker].

    Percent of the last ``lookback`` BBW values that are <= the current one.
    Mirrors the script exactly, including its shorter window while fewer
    than ``lookback`` bars exist. ``bbwp_ma`` is the script's SMA(5) line.
    """
    n = int(length)
    lb = int(lookback)
    basis = ma_2d(close, n, ma_type, volume)
    dev = k.stdev_nb(close, n)
    w = safe_div(2 * dev, basis)
    out = _bbwp_nb(w, n, lb)
    return out, k.sma_nb(out, int(ma_length))


@indicator("DOUBLE_BBANDS", ["close"], ["upper2", "upper1", "basis", "lower1", "lower2"])
def double_bbands(close, length=20, mult_inner=1.0, mult_outer=2.0):
    """Double Bollinger Bands (Kathy Lien): bands at 1 and 2 standard deviations."""
    basis, u1, l1 = _bb(close, length, mult_inner)
    _, u2, l2 = _bb(close, length, mult_outer)
    return u2, u1, basis, l1, l2


def _squeeze_momentum(high, low, close, n):
    """Carter's momentum: linreg(close - avg(donchian mid, sma), n, 0)."""
    mid = (k.highest_nb(high, n) + k.lowest_nb(low, n)) / 2
    return k.linreg_nb(close - (mid + k.sma_nb(close, n)) / 2, n, 0)


@indicator("SQUEEZE_MOMENTUM", ["high", "low", "close"],
           ["momentum", "sqz_on", "sqz_off", "no_sqz"])
def squeeze_momentum(high, low, close, bb_length=20, bb_mult=2.0, kc_length=20,
                     kc_mult=1.5, use_true_range=True, lazybear_compat=True):
    """Squeeze Momentum Indicator [LazyBear] - the most-liked TV script.

    ``lazybear_compat=True`` keeps the original script's quirk where the BB
    deviation uses ``kc_mult`` instead of ``bb_mult``, so values match the
    published chart. Set it to False for the intended 2.0-stdev bands.
    The KC range is ``sma(tr)`` (or ``sma(high-low)``), not ATR.
    """
    bn, kn = int(bb_length), int(kc_length)
    basis = k.sma_nb(close, bn)
    dev = (kc_mult if lazybear_compat else bb_mult) * k.stdev_nb(close, bn)
    upper_bb, lower_bb = basis + dev, basis - dev
    kc_mid = k.sma_nb(close, kn)
    rng = k.tr_nb(high, low, close, False) if use_true_range else high - low
    rangema = k.sma_nb(rng, kn)
    upper_kc, lower_kc = kc_mid + rangema * kc_mult, kc_mid - rangema * kc_mult
    sqz_on = (lower_bb > lower_kc) & (upper_bb < upper_kc)
    sqz_off = (lower_bb < lower_kc) & (upper_bb > upper_kc)
    no_sqz = ~sqz_on & ~sqz_off
    return _squeeze_momentum(high, low, close, kn), sqz_on, sqz_off, no_sqz


@indicator("TTM_SQUEEZE", ["high", "low", "close"],
           ["momentum", "no_sqz", "low_sqz", "mid_sqz", "high_sqz"])
def ttm_squeeze(high, low, close, length=20, bb_mult=2.0, kc_mult_high=1.0,
                kc_mult_mid=1.5, kc_mult_low=2.0):
    """TTM Squeeze Pro [Beardy_Fred]: BB(20, 2) against KC at 1.0/1.5/2.0.

    KC basis is SMA(close) and its range is SMA(true range), as in the script.
    ``mid_sqz`` is the classic John Carter TTM squeeze (KC 1.5).
    The ``or`` conditions are copied from the script verbatim.
    """
    n = int(length)
    basis = k.sma_nb(close, n)
    dev = bb_mult * k.stdev_nb(close, n)
    bb_u, bb_l = basis + dev, basis - dev
    dev_kc = k.sma_nb(k.tr_nb(high, low, close, False), n)

    def inside(m):
        return (bb_l >= basis - dev_kc * m) | (bb_u <= basis + dev_kc * m)

    no_sqz = (bb_l < basis - dev_kc * kc_mult_low) | (bb_u > basis + dev_kc * kc_mult_low)
    return (_squeeze_momentum(high, low, close, n), no_sqz,
            inside(kc_mult_low), inside(kc_mult_mid), inside(kc_mult_high))


@njit(cache=True)
def _bbwp_nb(w, n, lookback):
    out = np.full(w.shape, np.nan)
    for c in range(w.shape[1]):
        for i in range(n, w.shape[0]):
            ln = i if i < lookback else lookback
            if ln == 0 or np.isnan(w[i, c]):
                continue
            s = 0.0
            for j in range(1, ln + 1):
                # (bbw[j] > bbw ? 0 : 1); a comparison with na is false -> 1
                s += 0.0 if w[i - j, c] > w[i, c] else 1.0
            out[i, c] = s / ln * 100
    return out
