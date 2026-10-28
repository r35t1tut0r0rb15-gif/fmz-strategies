"""More momentum oscillators (TradingView built-ins and well-known scripts)."""

import numpy as np
from numba import njit

from . import kernels as k
from ._core import change_2d, indicator, ma_2d, safe_div, shift_2d
from .oscillators import rsi_2d
from .volatility import atr_2d

NAN = np.nan


def _roc(x, n):
    p = shift_2d(x, int(n))
    return safe_div(x - p, p) * 100


def _swma(x):
    return (x + 2 * shift_2d(x, 1) + 2 * shift_2d(x, 2) + shift_2d(x, 3)) / 6


@njit(cache=True)
def _csf_nb(src, n):
    """DecisionPoint custom smoothing: sm := na(sm[1]) ? src : sm[1] + (src - sm[1]) * 2/n."""
    out = np.full(src.shape, NAN)
    a = 2.0 / n
    for c in range(src.shape[1]):
        prev = NAN
        for i in range(src.shape[0]):
            v = src[i, c]
            cur = v if np.isnan(prev) else (v - prev) * a + prev
            out[i, c] = cur
            prev = cur
    return out


@indicator("PPO", ["close"], ["ppo", "signal", "hist"])
def ppo(close, fast=12, slow=26, signal=9, ma_type="ema"):
    """Percentage Price Oscillator: 100 * (fast MA - slow MA) / slow MA."""
    s = ma_2d(close, slow, ma_type)
    p = safe_div(ma_2d(close, fast, ma_type) - s, s) * 100
    sig = k.ema_nb(p, int(signal))
    return p, sig, p - sig


@indicator("APO", ["close"], ["apo"])
def apo(close, fast=12, slow=26, ma_type="ema"):
    """Absolute Price Oscillator: fast MA - slow MA."""
    return ma_2d(close, fast, ma_type) - ma_2d(close, slow, ma_type)


@indicator("PRICE_OSC", ["close"], ["po"])
def price_oscillator(close, short_length=10, long_length=21, exponential=False):
    """Price Oscillator (TradingView built-in, 10 / 21, SMA): (short-long)/long*100."""
    t = "ema" if exponential else "sma"
    lng = ma_2d(close, long_length, t)
    return safe_div(ma_2d(close, short_length, t) - lng, lng) * 100


@indicator("KST", ["close"], ["kst", "signal"])
def kst(close, roc1=10, roc2=15, roc3=20, roc4=30, sma1=10, sma2=10, sma3=10, sma4=15, signal=9):
    """Know Sure Thing (TradingView built-in)."""
    v = (k.sma_nb(_roc(close, roc1), int(sma1)) + 2 * k.sma_nb(_roc(close, roc2), int(sma2))
         + 3 * k.sma_nb(_roc(close, roc3), int(sma3)) + 4 * k.sma_nb(_roc(close, roc4), int(sma4)))
    return v, k.sma_nb(v, int(signal))


@indicator("RVGI", ["open", "high", "low", "close"], ["rvgi", "signal"])
def rvgi(open, high, low, close, length=10):
    """Relative Vigor Index (TradingView built-in, 10)."""
    n = int(length)
    r = safe_div(k.sum_nb(_swma(close - open), n), k.sum_nb(_swma(high - low), n))
    return r, _swma(r)


@indicator("RVI", ["close"], ["rvi"])
def relative_volatility_index(close, stdev_length=10, ema_length=14):
    """Relative Volatility Index (TradingView built-in, 10 / 14)."""
    sd = k.stdev_nb(close, int(stdev_length))
    ch = change_2d(close)
    with np.errstate(invalid="ignore"):
        up = k.ema_nb(np.where(ch <= 0, 0.0, sd), int(ema_length))
        dn = k.ema_nb(np.where(ch > 0, 0.0, sd), int(ema_length))
    # Pine compares na as false, so the first bar uses stdev (na) in both legs
    return safe_div(up, up + dn) * 100


@indicator("SMI_ERGODIC", ["close"], ["smi", "signal", "oscillator"])
def smi_ergodic(close, long_length=20, short_length=5, signal_length=5):
    """SMI Ergodic Indicator / Oscillator (TradingView built-ins).

    ``smi`` = ta.tsi(close, 5, 20) on the -1..1 scale, signal = ema(smi, 5),
    oscillator = smi - signal.
    """
    pc = change_2d(close)
    num = k.ema_nb(k.ema_nb(pc, int(long_length)), int(short_length))
    den = k.ema_nb(k.ema_nb(np.abs(pc), int(long_length)), int(short_length))
    e = safe_div(num, den)
    s = k.ema_nb(e, int(signal_length))
    return e, s, e - s


@indicator("SMI", ["high", "low", "close"], ["smi", "signal", "ema"])
def smi(high, low, close, k_length=10, d_length=3, ema_length=10):
    """Stochastic Momentum Index (Blau), as in the popular [UCSgears] script."""
    a, b = int(k_length), int(d_length)
    hh = k.highest_nb(high, a)
    ll = k.lowest_nb(low, a)
    rel = k.ema_nb(k.ema_nb(close - (hh + ll) / 2, b), b)
    dif = k.ema_nb(k.ema_nb(hh - ll, b), b)
    with np.errstate(divide="ignore", invalid="ignore"):
        s = np.where(dif != 0, rel / (dif / 2) * 100, 0.0)
    s[np.isnan(dif)] = NAN
    return s, k.ema_nb(s, b), k.ema_nb(s, int(ema_length))


@indicator("BULL_BEAR_POWER", ["high", "low", "close"], ["bull", "bear", "bbp"])
def bull_bear_power(high, low, close, length=13):
    """Elder-Ray Bull/Bear Power; ``bbp`` = their sum (TV's "Bull Bear Power")."""
    e = k.ema_nb(close, int(length))
    return high - e, low - e, (high - e) + (low - e)


@indicator("BOP", ["open", "high", "low", "close"], ["bop"])
def bop(open, high, low, close):
    """Balance of Power: (close-open)/(high-low); na when high == low."""
    return safe_div(close - open, high - low)


@indicator("QSTICK", ["open", "close"], ["qstick"])
def qstick(open, close, length=8):
    """Qstick (Chande): sma(close - open, length)."""
    return k.sma_nb(close - open, int(length))


@indicator("MASS_INDEX", ["high", "low"], ["mass"])
def mass_index(high, low, length=10):
    """Mass Index (TradingView built-in, 10; EMA 9)."""
    e1 = k.ema_nb(high - low, 9)
    return k.sum_nb(safe_div(e1, k.ema_nb(e1, 9)), int(length))


@indicator("ULCER", ["close"], ["ulcer"])
def ulcer_index(close, length=14):
    """Ulcer Index: RMS of % drawdown from the rolling ``length`` high."""
    n = int(length)
    hh = k.highest_nb(close, n)
    dd = safe_div(close - hh, hh) * 100
    return np.sqrt(k.sma_nb(dd * dd, n))


@indicator("CHAIKIN_VOL", ["high", "low"], ["chaikin_vol"])
def chaikin_volatility(high, low, ema_length=10, roc_length=10):
    """Chaikin Volatility: % change of ema(high-low) over ``roc_length`` bars."""
    return _roc(k.ema_nb(high - low, int(ema_length)), roc_length)


@indicator("ER", ["close"], ["er"])
def efficiency_ratio(close, length=10):
    """Kaufman Efficiency Ratio: |net change| / sum of |bar changes| (0..1)."""
    n = int(length)
    return safe_div(np.abs(change_2d(close, n)), k.sum_nb(np.abs(change_2d(close)), n))


@indicator("VHF", ["close"], ["vhf"])
def vhf(close, length=28):
    """Vertical Horizontal Filter."""
    n = int(length)
    rng = k.highest_nb(close, n) - k.lowest_nb(close, n)
    return safe_div(rng, k.sum_nb(np.abs(change_2d(close)), n))


@indicator("TREND_STRENGTH", ["close"], ["tsi"])
def trend_strength_index(close, length=14):
    """Trend Strength Index (TradingView built-in): correlation(close, bar_index)."""
    t = np.broadcast_to(np.arange(close.shape[0], dtype=float).reshape(-1, 1), close.shape)
    return k.correlation_nb(close, np.ascontiguousarray(t), int(length))


@indicator("RCI", ["close"], ["rci"])
def rci(close, length=9):
    """Rank Correlation Index (``ta.rci``), -100..100."""
    return k.rci_nb(close, int(length))


@indicator("PMO", ["close"], ["pmo", "signal"])
def pmo(close, length1=35, length2=20, signal=10):
    """DecisionPoint Price Momentum Oscillator: csf(10*csf(roc1, 35), 20)."""
    r = _roc(close, 1)
    p = _csf_nb(10 * _csf_nb(r, float(length1)), float(length2))
    return p, k.ema_nb(p, int(signal))


@indicator("IFISH_RSI", ["close"], ["ifish"])
def inverse_fisher_rsi(close, rsi_length=5, wma_length=9):
    """Inverse Fisher Transform of RSI (Ehlers): -1..1."""
    v = k.wma_nb(0.1 * (rsi_2d(close, int(rsi_length)) - 50), int(wma_length))
    e = np.exp(2 * v)
    return (e - 1) / (e + 1)


@indicator("TDI", ["close"], ["price_line", "signal_line", "mid", "upper", "lower"])
def tdi(close, rsi_length=13, band_length=34, band_mult=1.6185, fast=2, slow=7):
    """Traders Dynamic Index (Dean Malone): RSI 13, bands 34 x 1.6185, MAs 2 / 7."""
    r = rsi_2d(close, int(rsi_length))
    mid = k.sma_nb(r, int(band_length))
    dev = band_mult * k.stdev_nb(r, int(band_length))
    return k.sma_nb(r, int(fast)), k.sma_nb(r, int(slow)), mid, mid + dev, mid - dev


@indicator("MACD_V", ["high", "low", "close"], ["macd_v", "signal", "hist"])
def macd_v(high, low, close, fast=12, slow=26, signal=9, atr_length=26):
    """MACD-V (Alex Spiroglou): MACD / ATR(26) * 100."""
    m = safe_div(k.ema_nb(close, int(fast)) - k.ema_nb(close, int(slow)),
                 atr_2d(high, low, close, int(atr_length))) * 100
    s = k.ema_nb(m, int(signal))
    return m, s, m - s


@indicator("EWO", ["close"], ["ewo"])
def elliott_wave_oscillator(close, fast=5, slow=35, percent=False):
    """Elliott Wave Oscillator: sma(5) - sma(35), optionally as % of close."""
    d = k.sma_nb(close, int(fast)) - k.sma_nb(close, int(slow))
    return safe_div(d, close) * 100 if percent else d


@indicator("RMI", ["close"], ["rmi"])
def rmi(close, length=20, momentum=5):
    """Relative Momentum Index: RSI built on ``change(close, momentum)``."""
    ch = change_2d(close, int(momentum))
    up = k.rma_nb(np.maximum(ch, 0), int(length))
    dn = k.rma_nb(-np.minimum(ch, 0), int(length))
    with np.errstate(divide="ignore", invalid="ignore"):
        out = 100 - 100 / (1 + up / dn)
    out = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, out))
    out[np.isnan(up) | np.isnan(dn)] = NAN
    return out


@indicator("DEMARKER", ["high", "low"], ["demarker"])
def demarker(high, low, length=14):
    """DeMarker (0..1)."""
    n = int(length)
    dh = change_2d(high)
    dl = -change_2d(low)
    with np.errstate(invalid="ignore"):
        demax = k.sma_nb(np.where(np.isnan(dh), NAN, np.where(dh > 0, dh, 0.0)), n)
        demin = k.sma_nb(np.where(np.isnan(dl), NAN, np.where(dl > 0, dl, 0.0)), n)
    return safe_div(demax, demax + demin)


@indicator("PSY", ["close"], ["psy"])
def psychological_line(close, length=12):
    """Psychological Line: % of the last ``length`` bars that closed up."""
    ch = change_2d(close)
    with np.errstate(invalid="ignore"):
        up = np.where(np.isnan(ch), NAN, (ch > 0).astype(float))
    return k.sum_nb(up, int(length)) / int(length) * 100


@indicator("DISPARITY", ["close"], ["disparity"])
def disparity_index(close, length=14, ma_type="sma"):
    """Disparity Index: 100 * (close - MA) / MA."""
    m = ma_2d(close, length, ma_type)
    return safe_div(close - m, m) * 100


@indicator("AC", ["high", "low"], ["ac"])
def accelerator_oscillator(high, low):
    """Accelerator Oscillator (TradingView built-in): AO - sma(AO, 5)."""
    src = (high + low) / 2
    ao = k.sma_nb(src, 5) - k.sma_nb(src, 34)
    return ao - k.sma_nb(ao, 5)


@indicator("ELDER_IMPULSE", ["close"], ["impulse"])
def elder_impulse(close, ema_length=13, fast=12, slow=26, signal=9):
    """Elder Impulse System: 1 (green) when EMA and MACD histogram both rise,
    -1 (red) when both fall, 0 (blue) otherwise."""
    e = k.ema_nb(close, int(ema_length))
    m = k.ema_nb(close, int(fast)) - k.ema_nb(close, int(slow))
    hist = m - k.ema_nb(m, int(signal))
    de, dh = change_2d(e), change_2d(hist)
    with np.errstate(invalid="ignore"):
        out = np.where((de > 0) & (dh > 0), 1.0, np.where((de < 0) & (dh < 0), -1.0, 0.0))
    out[np.isnan(de) | np.isnan(dh)] = NAN
    return out


@indicator("CFO", ["close"], ["cfo"])
def chande_forecast_oscillator(close, length=14):
    """Chande Forecast Oscillator: 100 * (close - linreg(close, n)) / close."""
    return safe_div(close - k.linreg_nb(close, int(length), 0), close) * 100


@indicator("PGO", ["high", "low", "close"], ["pgo"])
def pretty_good_oscillator(high, low, close, length=14):
    """Pretty Good Oscillator (Mark Johnson): (close - sma) / ema(true range)."""
    n = int(length)
    return safe_div(close - k.sma_nb(close, n), k.ema_nb(k.tr_nb(high, low, close, True), n))


@indicator("IMI", ["open", "close"], ["imi"])
def intraday_momentum_index(open, close, length=14):
    """Intraday Momentum Index (Chande): RSI-style ratio of close-open moves."""
    n = int(length)
    d = close - open
    gains = k.sum_nb(np.where(d > 0, d, 0.0), n)
    losses = k.sum_nb(np.where(d < 0, -d, 0.0), n)
    return safe_div(gains, gains + losses) * 100


@indicator("RWI", ["high", "low", "close"], ["rwi_high", "rwi_low"])
def random_walk_index(high, low, close, length=14):
    """Random Walk Index: (high - low[n]) / (atr(n) * sqrt(n)) and the mirror."""
    n = int(length)
    den = atr_2d(high, low, close, n) * np.sqrt(n)
    return safe_div(high - shift_2d(low, n), den), safe_div(shift_2d(high, n) - low, den)
