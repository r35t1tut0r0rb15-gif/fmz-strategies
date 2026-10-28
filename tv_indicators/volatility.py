"""Volatility measures, channels and ATR-based stops."""

import numpy as np

from . import kernels as k
from ._core import indicator, ma_2d, safe_div, shift_2d


def atr_2d(high, low, close, length, smoothing="rma"):
    """``ta.atr`` when smoothing is RMA; TV's ATR indicator also offers SMA/EMA/WMA."""
    return ma_2d(k.tr_nb(high, low, close, True), int(length), smoothing)


@indicator("TR", ["high", "low", "close"], ["tr"])
def true_range(high, low, close, handle_na=True):
    """``ta.tr(handle_na)``; ``handle_na=True`` gives high-low on the first bar."""
    return k.tr_nb(high, low, close, bool(handle_na))


@indicator("ATR", ["high", "low", "close"], ["atr"])
def atr(high, low, close, length=14, smoothing="rma"):
    """Average True Range (TradingView built-in, default RMA 14)."""
    return atr_2d(high, low, close, length, smoothing)


@indicator("NATR", ["high", "low", "close"], ["natr"])
def natr(high, low, close, length=14):
    """Normalized ATR: 100 * ATR / close."""
    return safe_div(atr_2d(high, low, close, length), close) * 100


@indicator("HV", ["close"], ["hv"])
def historical_volatility(close, length=10, annual=365, per=1):
    """Historical Volatility (TradingView built-in).

    100 * stdev(ln(close/close[1]), length) * sqrt(annual/per).
    TradingView uses annual=365 and per=1 on intraday/daily charts, per=7
    on weekly and above.
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.log(close / shift_2d(close, 1))
    return 100 * k.stdev_nb(r, int(length)) * np.sqrt(annual / per)


@indicator("KC", ["high", "low", "close"], ["basis", "upper", "lower"])
def keltner(high, low, close, length=20, mult=2.0, use_ema=True,
            bands_style="atr", atr_length=10):
    """Keltner Channels (TradingView built-in).

    Defaults: length 20, multiplier 2, EMA basis, bands style
    "Average True Range" with ATR length 10. ``bands_style`` may be
    "atr", "tr" (true range) or "range" (rma(high-low, length)).
    """
    n = int(length)
    basis = k.ema_nb(close, n) if use_ema else k.sma_nb(close, n)
    style = str(bands_style).lower()
    if style in ("atr", "average true range"):
        rng = atr_2d(high, low, close, int(atr_length))
    elif style in ("tr", "true range"):
        rng = k.tr_nb(high, low, close, True)
    elif style == "range":
        rng = k.rma_nb(high - low, n)
    else:
        raise ValueError("bands_style must be 'atr', 'tr' or 'range'")
    return basis, basis + rng * mult, basis - rng * mult


@indicator("DONCHIAN", ["high", "low"], ["basis", "upper", "lower"])
def donchian(high, low, length=20):
    """Donchian Channels (TradingView built-in)."""
    n = int(length)
    upper = k.highest_nb(high, n)
    lower = k.lowest_nb(low, n)
    return (upper + lower) / 2, upper, lower


@indicator("ENVELOPE", ["close"], ["basis", "upper", "lower"])
def envelope(close, length=20, percent=10.0, exponential=False):
    """Envelope (TradingView built-in): basis * (1 +/- percent/100)."""
    n = int(length)
    basis = k.ema_nb(close, n) if exponential else k.sma_nb(close, n)
    kk = percent / 100.0
    return basis, basis * (1 + kk), basis * (1 - kk)


@indicator("CHANDELIER_EXIT", ["high", "low", "close"],
           ["long_stop", "short_stop", "direction", "buy", "sell"])
def chandelier_exit(high, low, close, length=22, mult=3.0, use_close=True):
    """Chandelier Exit [everget] - the popular TradingView version.

    ``direction`` is 1 while long, -1 while short; ``buy``/``sell`` mark flips.
    """
    n = int(length)
    a = mult * atr_2d(high, low, close, n)
    hb = k.highest_nb(close if use_close else high, n)
    lb = k.lowest_nb(close if use_close else low, n)
    return k.chandelier_nb(hb, lb, a, close)


@indicator("SUPERTREND", ["high", "low", "close"], ["supertrend", "direction", "trend"])
def supertrend(high, low, close, factor=3.0, atr_period=10):
    """``ta.supertrend(factor, atrPeriod)`` (TradingView built-in, 3 / 10).

    ``direction`` uses TradingView's convention (-1 = up trend, 1 = down
    trend). ``trend`` is the flipped, friendlier version: 1 up, -1 down.
    """
    src = (high + low) / 2
    a = atr_2d(high, low, close, int(atr_period))
    st, d = k.supertrend_nb(src, close, a, float(factor))
    return st, d, -d


@indicator("UT_BOT", ["high", "low", "close"], ["trailing_stop", "position", "buy", "sell"])
def ut_bot(high, low, close, key_value=1.0, atr_period=10):
    """UT Bot Alerts [QuantNomad] on regular candles.

    For the Heikin Ashi option, pass HA candles from :func:`heikin_ashi`
    as ``close`` (the script only swaps the source; ATR stays on the chart's
    high/low/close).
    """
    a = atr_2d(high, low, close, int(atr_period))
    stop, pos = k.utbot_nb(close, key_value * a)
    prev_c, prev_s = shift_2d(close, 1), shift_2d(stop, 1)
    above = (close > stop) & (prev_c <= prev_s)  # ta.crossover(ema(src,1), stop)
    below = (stop > close) & (prev_s <= prev_c)
    return stop, pos, (close > stop) & above, (close < stop) & below


@indicator("PSAR", ["high", "low", "close"], ["psar", "direction"])
def psar(high, low, close, start=0.02, increment=0.02, maximum=0.2):
    """Parabolic SAR = ``ta.sar(start, inc, max)`` (TradingView built-in).

    ``direction`` is 1 when SAR is below price (long), -1 when above.
    """
    s = k.sar_nb(high, low, close, float(start), float(increment), float(maximum))
    d = np.where(np.isnan(s), np.nan, np.where(s < close, 1.0, -1.0))
    return s, d


@indicator("CHOP", ["high", "low", "close"], ["chop"])
def choppiness(high, low, close, length=14):
    """Choppiness Index (TradingView built-in)."""
    n = int(length)
    tr = k.tr_nb(high, low, close, True)  # ta.atr(1)
    rng = k.highest_nb(high, n) - k.lowest_nb(low, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = 100 * np.log10(k.sum_nb(tr, n) / rng) / np.log10(n)
    out[~np.isfinite(out)] = np.nan
    return out


@indicator("VORTEX", ["high", "low", "close"], ["vi_plus", "vi_minus"])
def vortex(high, low, close, length=14):
    """Vortex Indicator (TradingView built-in)."""
    n = int(length)
    vmp = k.sum_nb(np.abs(high - shift_2d(low, 1)), n)
    vmm = k.sum_nb(np.abs(low - shift_2d(high, 1)), n)
    st = k.sum_nb(k.tr_nb(high, low, close, True), n)
    return safe_div(vmp, st), safe_div(vmm, st)


@indicator("HEIKIN_ASHI", ["open", "high", "low", "close"], ["open", "high", "low", "close"])
def heikin_ashi(open, high, low, close):
    """Heikin Ashi candles."""
    return k.heikin_ashi_nb(open, high, low, close)

