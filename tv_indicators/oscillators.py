"""Momentum oscillators."""

import numpy as np

from . import kernels as k
from ._core import change_2d, indicator, ma_2d, safe_div, shift_2d


def rsi_2d(x, n):
    """``ta.rsi``: Wilder RMA of gains / losses."""
    ch = change_2d(x)
    up = k.rma_nb(np.maximum(ch, 0), n)
    down = k.rma_nb(-np.minimum(ch, 0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = 100 - 100 / (1 + up / down)
    out = np.where(down == 0, 100.0, np.where(up == 0, 0.0, out))
    out[np.isnan(up) | np.isnan(down)] = np.nan
    return out


def stoch_2d(src, high, low, n):
    """``ta.stoch(source, high, low, length)``."""
    ll = k.lowest_nb(low, n)
    return safe_div(src - ll, k.highest_nb(high, n) - ll) * 100


@indicator("RSI", ["close"], ["rsi"])
def rsi(close, length=14):
    """Relative Strength Index (TradingView built-in, 14)."""
    return rsi_2d(close, int(length))


@indicator("STOCH", ["high", "low", "close"], ["k", "d"])
def stoch(high, low, close, k_length=14, k_smoothing=1, d_smoothing=3):
    """Stochastic (TradingView built-in: %K length 14, %K smoothing 1, %D 3)."""
    kk = k.sma_nb(stoch_2d(close, high, low, int(k_length)), int(k_smoothing))
    return kk, k.sma_nb(kk, int(d_smoothing))


@indicator("STOCH_RSI", ["close"], ["k", "d"])
def stoch_rsi(close, rsi_length=14, stoch_length=14, k_smoothing=3, d_smoothing=3):
    """Stochastic RSI (TradingView built-in: 3, 3, 14, 14)."""
    r = rsi_2d(close, int(rsi_length))
    kk = k.sma_nb(stoch_2d(r, r, r, int(stoch_length)), int(k_smoothing))
    return kk, k.sma_nb(kk, int(d_smoothing))


@indicator("MACD", ["close"], ["macd", "signal", "hist"])
def macd(close, fast=12, slow=26, signal=9, osc_ma="ema", signal_ma="ema"):
    """MACD (TradingView built-in: 12, 26, 9, EMA/EMA)."""
    m = ma_2d(close, fast, osc_ma) - ma_2d(close, slow, osc_ma)
    s = ma_2d(m, signal, signal_ma)
    return m, s, m - s


@indicator("CCI", ["close"], ["cci"])
def cci(close, length=20):
    """Commodity Channel Index. TradingView's default source is ``hlc3``."""
    n = int(length)
    return safe_div(close - k.sma_nb(close, n), 0.015 * k.dev_nb(close, n))


@indicator("WILLR", ["high", "low", "close"], ["willr"])
def willr(high, low, close, length=14):
    """Williams %R (TradingView built-in, -100..0)."""
    n = int(length)
    hh = k.highest_nb(high, n)
    return safe_div(close - hh, hh - k.lowest_nb(low, n)) * 100


@indicator("MFI", ["high", "low", "close", "volume"], ["mfi"])
def mfi(high, low, close, volume, length=14):
    """Money Flow Index = ``ta.mfi(hlc3, length)`` (TradingView built-in, 14)."""
    n = int(length)
    src = (high + low + close) / 3
    ch = change_2d(src)
    flow = volume * src
    # Pine: na comparisons are false, so the first bar counts in both sums.
    with np.errstate(invalid="ignore"):
        upper = k.sum_nb(np.where(ch <= 0, 0.0, flow), n)
        lower = k.sum_nb(np.where(ch >= 0, 0.0, flow), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = 100.0 - 100.0 / (1.0 + upper / lower)
    out = np.where(lower == 0, 100.0, out)  # Pine: x/0 = inf -> 100
    out[np.isnan(upper) | np.isnan(lower)] = np.nan
    return out


@indicator("ROC", ["close"], ["roc"])
def roc(close, length=9):
    """Rate of Change (TradingView built-in, 9)."""
    p = shift_2d(close, int(length))
    return safe_div(close - p, p) * 100


@indicator("MOM", ["close"], ["mom"])
def mom(close, length=10):
    """Momentum = close - close[length] (TradingView built-in, 10)."""
    return change_2d(close, int(length))


@indicator("AO", ["high", "low"], ["ao"])
def awesome_oscillator(high, low, fast=5, slow=34):
    """Awesome Oscillator: sma(hl2, 5) - sma(hl2, 34)."""
    src = (high + low) / 2
    return k.sma_nb(src, int(fast)) - k.sma_nb(src, int(slow))


@indicator("TSI", ["close"], ["tsi", "signal"])
def tsi(close, long_length=25, short_length=13, signal_length=13):
    """True Strength Index (TradingView built-in: 25 / 13 / 13, x100 scale)."""
    pc = change_2d(close)
    num = k.ema_nb(k.ema_nb(pc, int(long_length)), int(short_length))
    den = k.ema_nb(k.ema_nb(np.abs(pc), int(long_length)), int(short_length))
    t = safe_div(num, den) * 100
    return t, k.ema_nb(t, int(signal_length))


@indicator("CMO", ["close"], ["cmo"])
def cmo(close, length=9):
    """Chande Momentum Oscillator (TradingView built-in, plain sums, 9).

    Note TA-Lib's CMO uses Wilder smoothing instead and will not match.
    """
    n = int(length)
    m = change_2d(close)
    s1 = k.sum_nb(np.where(m >= 0, m, 0.0) + m * 0, n)  # keep na from m
    s2 = k.sum_nb(np.where(m >= 0, 0.0, -m) + m * 0, n)
    return safe_div(s1 - s2, s1 + s2) * 100


@indicator("UO", ["high", "low", "close"], ["uo"])
def ultimate_oscillator(high, low, close, fast=7, middle=14, slow=28):
    """Ultimate Oscillator (TradingView built-in: 7 / 14 / 28)."""
    pc = shift_2d(close, 1)
    hi = np.fmax(high, pc)  # math.max(high, close[1]); first bar uses high
    lo = np.fmin(low, pc)
    hi[np.isnan(pc)] = np.nan
    lo[np.isnan(pc)] = np.nan
    bp = close - lo
    tr = hi - lo

    def avg(n):
        return safe_div(k.sum_nb(bp, int(n)), k.sum_nb(tr, int(n)))

    return 100 * (4 * avg(fast) + 2 * avg(middle) + avg(slow)) / 7


@indicator("FISHER", ["high", "low"], ["fisher", "trigger"])
def fisher(high, low, length=9):
    """Fisher Transform (TradingView built-in, 9). ``trigger`` = fisher[1]."""
    src = (high + low) / 2
    n = int(length)
    return k.fisher_nb(src, k.highest_nb(src, n), k.lowest_nb(src, n))


@indicator("TRIX", ["close"], ["trix"])
def trix(close, length=18):
    """TRIX (TradingView built-in): 10000 * change(log(ema(ema(ema(close)))))."""
    n = int(length)
    e3 = k.ema_nb(k.ema_nb(k.ema_nb(close, n), n), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        return 10000 * change_2d(np.log(e3))


@indicator("WAVETREND", ["high", "low", "close"], ["wt1", "wt2"])
def wavetrend(high, low, close, channel_length=10, average_length=21, signal_length=4):
    """WaveTrend Oscillator [LazyBear] (channel 10, average 21, signal SMA 4)."""
    ap = (high + low + close) / 3
    n1 = int(channel_length)
    esa = k.ema_nb(ap, n1)
    d = k.ema_nb(np.abs(ap - esa), n1)
    ci = safe_div(ap - esa, 0.015 * d)
    wt1 = k.ema_nb(ci, int(average_length))
    return wt1, k.sma_nb(wt1, int(signal_length))


@indicator("CRSI", ["close"], ["crsi"])
def connors_rsi(close, rsi_length=3, updown_length=2, roc_length=100):
    """Connors RSI (TradingView built-in: 3 / 2 / 100)."""
    r = rsi_2d(close, int(rsi_length))
    ud = rsi_2d(k.updown_nb(close), int(updown_length))
    pr = k.percentrank_nb(safe_div(change_2d(close), shift_2d(close, 1)) * 100, int(roc_length))
    return (r + ud + pr) / 3


@indicator("COPPOCK", ["close"], ["coppock"])
def coppock(close, wma_length=10, long_roc=14, short_roc=11):
    """Coppock Curve (TradingView built-in: 10 / 14 / 11)."""
    def _roc(n):
        p = shift_2d(close, n)
        return safe_div(close - p, p) * 100

    return k.wma_nb(_roc(int(long_roc)) + _roc(int(short_roc)), int(wma_length))


@indicator("DPO", ["close"], ["dpo"])
def dpo(close, length=21):
    """Detrended Price Oscillator, non-centered (TradingView's ``isCentered=false``).

    close - sma(close, length)[length/2 + 1]; no look-ahead, safe to backtest.
    """
    n = int(length)
    return close - shift_2d(k.sma_nb(close, n), n // 2 + 1)
