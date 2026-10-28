"""Rolling statistics, regression and range-based volatility estimators."""

import numpy as np

from . import kernels as k
from ._core import indicator, safe_div, shift_2d


@indicator("STDEV", ["close"], ["stdev"])
def stdev(close, length=20):
    """``ta.stdev`` (population)."""
    return k.stdev_nb(close, int(length))


@indicator("VARIANCE", ["close"], ["variance"])
def variance(close, length=20):
    """``ta.variance`` (population)."""
    return k.stdev_nb(close, int(length)) ** 2


@indicator("ZSCORE", ["close"], ["zscore"])
def zscore(close, length=20):
    """(close - sma) / stdev over ``length`` bars."""
    n = int(length)
    return safe_div(close - k.sma_nb(close, n), k.stdev_nb(close, n))


@indicator("PERCENTRANK", ["close"], ["percentrank"])
def percentrank(close, length=100):
    """``ta.percentrank``: % of the previous ``length`` values <= current."""
    return k.percentrank_nb(close, int(length))


@indicator("LINREG", ["close"], ["value", "slope", "intercept", "r2", "angle"])
def linreg(close, length=14):
    """Rolling linear regression of close on bar number.

    ``value`` = ta.linreg(close, n, 0); ``slope`` / ``intercept`` match
    TA-Lib's LINEARREG_SLOPE / LINEARREG_INTERCEPT (intercept is the value
    at the oldest bar of the window); ``angle`` is atan(slope) in degrees,
    as TA-Lib's LINEARREG_ANGLE; ``r2`` is the coefficient of determination.
    """
    n = int(length)
    slope, icpt, r2 = k.linreg_stats_nb(close, n)
    return icpt + slope * (n - 1), slope, icpt, r2, np.degrees(np.arctan(slope))


@indicator("CORREL", ["close", "other"], ["correl"])
def correlation(close, other, length=20):
    """``ta.correlation(close, other, length)`` (Pearson)."""
    return k.correlation_nb(close, other, int(length))


@indicator("BETA", ["close", "benchmark"], ["beta"])
def beta(close, benchmark, length=20):
    """Rolling beta of close's returns against the benchmark's returns."""
    n = int(length)
    r = safe_div(close, shift_2d(close, 1)) - 1
    b = safe_div(benchmark, shift_2d(benchmark, 1)) - 1
    mr, mb = k.sma_nb(r, n), k.sma_nb(b, n)
    cov = k.sma_nb(r * b, n) - mr * mb
    var = k.sma_nb(b * b, n) - mb * mb
    return safe_div(cov, var)


@indicator("RELATIVE_STRENGTH", ["close", "benchmark"], ["rs"])
def relative_strength(close, benchmark, length=55):
    """Relative Strength vs a benchmark [Modhelius]: (c/c[n]) / (b/b[n]) - 1."""
    n = int(length)
    return safe_div(safe_div(close, shift_2d(close, n)), safe_div(benchmark, shift_2d(benchmark, n))) - 1


def _annual(x, annual):
    return x * np.sqrt(annual)


@indicator("PARKINSON", ["high", "low"], ["parkinson"])
def parkinson(high, low, length=20, annual=1.0):
    """Parkinson volatility (per bar; ``annual`` = bars per year to annualize)."""
    hl = np.log(high / low) ** 2
    return _annual(np.sqrt(k.sma_nb(hl, int(length)) / (4 * np.log(2))), annual)


@indicator("GARMAN_KLASS", ["open", "high", "low", "close"], ["garman_klass"])
def garman_klass(open, high, low, close, length=20, annual=1.0):
    """Garman-Klass volatility."""
    v = 0.5 * np.log(high / low) ** 2 - (2 * np.log(2) - 1) * np.log(close / open) ** 2
    return _annual(np.sqrt(k.sma_nb(v, int(length))), annual)


@indicator("ROGERS_SATCHELL", ["open", "high", "low", "close"], ["rogers_satchell"])
def rogers_satchell(open, high, low, close, length=20, annual=1.0):
    """Rogers-Satchell volatility (handles drift)."""
    v = np.log(high / close) * np.log(high / open) + np.log(low / close) * np.log(low / open)
    return _annual(np.sqrt(k.sma_nb(v, int(length))), annual)


@indicator("YANG_ZHANG", ["open", "high", "low", "close"], ["yang_zhang"])
def yang_zhang(open, high, low, close, length=20, annual=1.0):
    """Yang-Zhang volatility (overnight + open-to-close + Rogers-Satchell)."""
    n = int(length)
    kk = 0.34 / (1.34 + (n + 1) / (n - 1))
    with np.errstate(divide="ignore", invalid="ignore"):
        on = np.log(open / shift_2d(close, 1))
    oc = np.log(close / open)
    sample = n / (n - 1)
    v_on = k.stdev_nb(on, n) ** 2 * sample
    v_oc = k.stdev_nb(oc, n) ** 2 * sample
    rs = np.log(high / close) * np.log(high / open) + np.log(low / close) * np.log(low / open)
    v = v_on + kk * v_oc + (1 - kk) * k.sma_nb(rs, n)
    return _annual(np.sqrt(v), annual)
