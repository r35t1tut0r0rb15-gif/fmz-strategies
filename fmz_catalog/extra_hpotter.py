"""Best-version code for the indicators inside HPotter's FMZ strategies.

HPotter is a prolific TradingView author who ported a large number of
Stocks & Commodities (TASC) and book indicators, often as the second half of
his "123 Reversal + X" combo strategies. This module implements every X that
``tv_indicators`` / ``fmz_catalog.extra`` lack, following the original
author's definition. Where HPotter's port legitimately simplifies the
original, ``hpotter=True`` reproduces his numbers bar for bar; where his port
has a bug, only the correct version is implemented (see
``scan/impl/hpotter_report.json`` for the bugs and the strategies they hit).

Like ``fmz_catalog.extra``, nothing here is wired into ``tv_indicators``:
importing the module moves its indicators into ``EXTRA_HPOTTER``.

    import fmz_catalog.extra_hpotter as hp
    fve = hp.finite_volume_elements(df.high, df.low, df.close, df.volume)
"""

import math

import numpy as np
from numba import njit

from tv_indicators import kernels as k
from tv_indicators._core import REGISTRY, change_2d, indicator, safe_div, shift_2d
from tv_indicators.oscillators import rsi_2d, stoch_2d
from tv_indicators.trend import dmi as _dmi
from tv_indicators.volatility import atr_2d

NAN = np.nan
_BEFORE = dict(REGISTRY)

# Pine's ``math.pi`` stand-ins used in HPotter's Ehlers ports.
_PI_BANDPASS_HP = 3.14     # Bandpass Filter strategies
_PI_EMD_HP = 3.1415        # Extracting the Trend / Empirical Mode Decomposition


def _gt(a, b):
    """Pine ``a > b`` (false when either side is na)."""
    with np.errstate(invalid="ignore"):
        return a > b


def _lt(a, b):
    with np.errstate(invalid="ignore"):
        return a < b


def _pine_round(x):
    """Pine ``round``: nearest integer, ties rounded up."""
    return np.floor(x + 0.5)


# ---------------------------------------------------------------------------
# nz()-seeded recursions (Pine ``x := f(nz(x[1]))``): na input -> na output,
# and the next bar restarts from the nz() seed.
# ---------------------------------------------------------------------------

@njit(cache=True)
def _nzcum_nb(term, seed):
    out = np.full(term.shape, NAN)
    for c in range(term.shape[1]):
        prev = NAN
        for i in range(term.shape[0]):
            p = seed if np.isnan(prev) else prev
            v = p + term[i, c]
            out[i, c] = v
            prev = v
    return out


@njit(cache=True)
def _wilder_nz_nb(x, n, seed):
    """y = ((n - 1) * nz(y[1], seed) + x) / n."""
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        prev = NAN
        for i in range(x.shape[0]):
            p = seed if np.isnan(prev) else prev
            v = ((n - 1.0) * p + x[i, c]) / n
            out[i, c] = v
            prev = v
    return out


@njit(cache=True)
def _ema_nz_nb(x, w):
    """y = w * x + (1 - w) * nz(y[1]) (zero-seeded EMA, as in T3-CCI)."""
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        prev = NAN
        for i in range(x.shape[0]):
            p = 0.0 if np.isnan(prev) else prev
            v = w * x[i, c] + (1.0 - w) * p
            out[i, c] = v
            prev = v
    return out


# ---------------------------------------------------------------------------
# Fractals, candle patterns and other bar-structure indicators
# ---------------------------------------------------------------------------

@njit(cache=True)
def _fractal_level_nb(x, p, up):
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        res = NAN
        for i in range(x.shape[0]):
            if i >= 2 * p + 1:
                ok = True
                for j in range(p, 0, -1):          # bars after the centre
                    a, b = x[i - j, c], x[i - j - 1, c]
                    ok = ok and ((a < b) if up else (a > b))
                for j in range(p + 2, 2 * p + 2):  # bars before the centre
                    a, b = x[i - j, c], x[i - j + 1, c]
                    ok = ok and ((a < b) if up else (a > b))
                if ok:
                    res = x[i - p - 1, c]
            out[i, c] = res
    return out


@indicator("FRACTAL_CHAOS_BANDS", ["high", "low"], ["upper", "lower"])
def fractal_chaos_bands(high, low, pattern=1):
    """Fractal Chaos Bands (Edward Dobson's band form of Bill Williams'
    fractals), as coded by HPotter.

    ``upper`` is the high of the last confirmed up-fractal (``pattern``
    strictly lower highs on each side of it), ``lower`` the low of the last
    down-fractal; both hold until the next fractal and are known on the bar
    that confirms the fractal (``pattern`` bars after the centre), so there
    is no look-ahead. ``pattern=2`` is Williams' 5-bar fractal with strict
    inequalities (TradingView's ``fractals`` allows some ties).
    """
    p = int(pattern)
    return _fractal_level_nb(high, p, True), _fractal_level_nb(low, p, False)


@indicator("FRACTAL_CHAOS_OSC", ["high", "low"], ["fco"])
def fractal_chaos_oscillator(high, low, pattern=1):
    """Fractal Chaos Oscillator: +1 on the bar a new up-fractal level appears,
    -1 for a new down-fractal level, else 0 (HPotter's port of the MetaStock
    indicator). A new level equal to the previous one does not count, and
    the first level after na does not count either (Pine na comparisons)."""
    p = int(pattern)
    up = _fractal_level_nb(high, p, True)
    dn = _fractal_level_nb(low, p, False)
    with np.errstate(invalid="ignore"):
        cu = (up != shift_2d(up, 1)) & ~np.isnan(up) & ~np.isnan(shift_2d(up, 1))
        cd = (dn != shift_2d(dn, 1)) & ~np.isnan(dn) & ~np.isnan(shift_2d(dn, 1))
    return np.where(cu, 1.0, np.where(cd, -1.0, 0.0))


@indicator("KEY_REVERSAL", ["high", "low", "close"], ["up", "down"])
def key_reversal(high, low, close, length=1):
    """Key reversal bars: ``up`` = low below the lowest low of the previous
    ``length`` bars and close above the previous close; ``down`` = high
    above the previous ``length``-bar high and close below the previous
    close (HPotter's Key Reversal Up/Down)."""
    n = int(length)
    ll = k.lowest_nb(shift_2d(low, 1), n)
    hh = k.highest_nb(shift_2d(high, 1), n)
    c1 = shift_2d(close, 1)
    return _lt(low, ll) & _gt(close, c1), _gt(high, hh) & _lt(close, c1)


@indicator("THREE_BAR_REVERSAL", ["open", "high", "low", "close"], ["bull", "bear"])
def three_bar_reversal(open, high, low, close):
    """3-Bar Reversal Pattern (HPotter): ``bull`` = bearish bar two bars ago,
    an inside-lower bar (lower high and lower low), then a bar with a higher
    high and higher low; ``bear`` is the mirror image."""
    o2, c2 = shift_2d(open, 2), shift_2d(close, 2)
    h1, h2, l1, l2 = shift_2d(high, 1), shift_2d(high, 2), shift_2d(low, 1), shift_2d(low, 2)
    bull = _gt(o2, c2) & _lt(h1, h2) & _lt(l1, l2) & _gt(low, l1) & _gt(high, h1)
    bear = _lt(o2, c2) & _gt(h1, h2) & _gt(l1, l2) & _lt(high, h1) & _lt(low, l1)
    return bull, bear


@njit(cache=True)
def _nbars_nb(open_, close, lag):
    up = np.full(close.shape, NAN)
    dn = np.full(close.shape, NAN)
    for c in range(close.shape[1]):
        u = 0.0
        d = 0.0
        for i in range(close.shape[0]):
            j = i - lag
            if j >= 0:
                o, cl = open_[j, c], close[j, c]
                if cl >= o:
                    u += 1.0
                elif cl < o:
                    u = 0.0
                if cl <= o:
                    d += 1.0
                elif cl > o:
                    d = 0.0
            up[i, c] = u
            dn[i, c] = d
    return up, dn


@indicator("N_BARS_UP_DOWN", ["open", "close"], ["up_count", "down_count"])
def n_bars_up_down(open, close, hpotter=False):
    """Run length of consecutive up bars (close >= open) and down bars
    (close <= open); a doji counts for both runs, as in HPotter's N Bars
    Up / N Bars Down. ``hpotter=True`` gives his counter, which counts the
    bars up to the previous bar (``close[1] >= open[1]``)."""
    return _nbars_nb(open, close, 1 if hpotter else 0)


@indicator("HARAMI", ["open", "close"], ["bull", "bear"])
def harami(open, close, min_body=0.0):
    """Bullish / bearish harami as in HPotter's Harami backtests: the current
    body (at least ``min_body``) lies inside the opposite-coloured previous
    body and is smaller than it."""
    o1, c1 = shift_2d(open, 1), shift_2d(close, 1)
    body = np.abs(close - open) >= min_body
    with np.errstate(invalid="ignore"):
        bull = body & (o1 > c1) & (close > open) & (close <= o1) & (c1 <= open) & (close - open < o1 - c1)
        bear = body & (c1 > o1) & (open > close) & (open <= c1) & (o1 <= close) & (open - close < c1 - o1)
    return bull, bear


@indicator("ENGULFING", ["open", "close"], ["bull", "bear"])
def engulfing(open, close, min_body=0.0):
    """Engulfing patterns as in HPotter's Bearish Engulfing backtest (the
    previous body must be at least ``min_body``); ``bull`` is the mirror."""
    o1, c1 = shift_2d(open, 1), shift_2d(close, 1)
    with np.errstate(invalid="ignore"):
        body = np.abs(c1 - o1) >= min_body
        bear = body & (c1 > o1) & (open > close) & (open >= c1) & (o1 >= close) & (open - close > c1 - o1)
        bull = body & (o1 > c1) & (close > open) & (close >= o1) & (c1 >= open) & (close - open > o1 - c1)
    return bull, bear


@indicator("THREE_INSIDE", ["open", "close"], ["up", "down"])
def three_inside(open, close):
    """Three Inside Up / Down (a harami confirmed by a third bar that closes
    beyond the first bar's open), as in HPotter's backtests."""
    o1, c1, o2, c2 = shift_2d(open, 1), shift_2d(close, 1), shift_2d(open, 2), shift_2d(close, 2)
    with np.errstate(invalid="ignore"):
        up = ((o2 > c2) & (c1 > o1) & (c1 <= o2) & (c2 <= o1) & (c1 - o1 < o2 - c2)
              & (close > open) & (close > c1) & (open > o1) & (close > o2))
        down = ((c2 > o2) & (o1 > c1) & (o1 <= c2) & (o2 <= c1) & (o1 - c1 < c2 - o2)
                & (close < open) & (close < c1) & (open < o1) & (close < o2))
    return up, down


@indicator("DOJI", ["open", "close"], ["doji"])
def doji(open, close, max_body=0.0):
    """Doji: body no larger than ``max_body`` (0 = open == close, which is
    what HPotter's Doji backtest effectively requires)."""
    return np.abs(close - open) <= max_body


@njit(cache=True)
def _period_hl_nb(high, low, sess, lookback):
    hi = np.full(high.shape, NAN)
    lo = np.full(high.shape, NAN)
    for c in range(high.shape[1]):
        hist_h = np.full(lookback + 1, NAN)   # [0] = current period so far
        hist_l = np.full(lookback + 1, NAN)
        for i in range(high.shape[0]):
            if i == 0 or sess[i, c] != sess[i - 1, c]:
                for j in range(lookback, 0, -1):
                    hist_h[j] = hist_h[j - 1]
                    hist_l[j] = hist_l[j - 1]
                hist_h[0] = NAN
                hist_l[0] = NAN
            h, l = high[i, c], low[i, c]
            if not np.isnan(h) and (np.isnan(hist_h[0]) or h > hist_h[0]):
                hist_h[0] = h
            if not np.isnan(l) and (np.isnan(hist_l[0]) or l < hist_l[0]):
                hist_l[0] = l
            hi[i, c] = hist_h[lookback]
            lo[i, c] = hist_l[lookback]
    return hi, lo


@indicator("PERIOD_HIGH_LOW", ["high", "low", "session"], ["high", "low"])
def period_high_low(high, low, session, lookback=1):
    """High and low of the calendar period ``lookback`` periods ago, i.e.
    ``request.security(tickerid, tf, high[lookback])`` without look-ahead.

    ``session`` holds one id per period (``tv_indicators.session_ids(index,
    "D")``, "W", ...). ``lookback=0`` gives the running high/low of the
    current period so far (HPotter's ``DayHigh``/``DayLow`` in Elder Ray).
    Used by HPotter's Cueing Off Support and Resistance Levels (weekly,
    lookback 1) and High and Low Levels (daily, lookback 1).
    """
    return _period_hl_nb(high, low, np.nan_to_num(session, nan=-1.0), int(lookback))


# ---------------------------------------------------------------------------
# Gimelfarb Bull / Bear Power and Bull and Bear Balance (TASC Oct 2003)
# ---------------------------------------------------------------------------

def _gimelfarb(open, high, low, close):
    o, h, l, c = open, high, low, close
    c1 = shift_2d(close, 1)
    mx = np.maximum
    with np.errstate(invalid="ignore"):
        bear = np.select(
            [c < o, c > o, h - c > c - l, h - c < c - l, c > o, c1 < o],
            [np.where(c1 > o, mx(c - o, h - l), h - l),
             np.where(c1 > o, mx(c1 - l, h - c), mx(o - l, h - c)),
             np.where(c1 > o, mx(c1 - o, h - l), h - l),
             np.where(c > o, mx(c - l, h - c), o - l),
             mx(c1 - o, h - c),
             mx(o - l, h - c)],
            h - l)
        bull = np.select(
            [c < o, c > o, h - c > c - l, h - c < c - l, c1 > o, c1 < o],
            [np.where(c1 < o, mx(h - c1, c - l), mx(h - o, c - l)),
             np.where(c1 > o, h - l, mx(o - c1, h - l)),
             np.where(c1 < o, mx(h - c1, c - l), h - o),
             np.where(c1 > o, h - l, mx(o - c, h - l)),
             mx(h - o, c - l),
             mx(o - c, h - l)],
            h - l)
    return bull, bear


@indicator("BULL_BEAR_BALANCE", ["open", "high", "low", "close"], ["bull", "bear", "balance"])
def bull_bear_balance(open, high, low, close, smooth=1):
    """Vadim Gimelfarb's Bull Power, Bear Power and Bull and Bear Balance
    (TASC Oct 2003, "Who's In Control?"), with HPotter's case table.

    ``balance`` = bull - bear. ``smooth`` > 1 applies an SMA to all three
    (the TradeStation Traders' Tip smoothed the balance with 30 bars;
    HPotter uses the raw values, smooth=1).
    """
    bull, bear = _gimelfarb(open, high, low, close)
    bal = bull - bear
    n = int(smooth)
    if n > 1:
        bull, bear, bal = k.sma_nb(bull, n), k.sma_nb(bear, n), k.sma_nb(bal, n)
    return bull, bear, bal


# ---------------------------------------------------------------------------
# Widner Rainbow, prime numbers
# ---------------------------------------------------------------------------

@indicator("RAINBOW_OSC", ["close"], ["rbo", "bandwidth"])
def rainbow_oscillator(close, length=2, levels=10, hhll_length=10):
    """Mel Widner's Rainbow Oscillator (TASC 1997): ``levels`` recursive
    SMAs of ``length``; rbo = 100 * (close - mean of the averages) /
    (HHV(close) - LLV(close)) and bandwidth = 100 * (max - min of the
    averages) / the same range. HPotter's port is faithful (2, 10, 10)."""
    m = close
    mas = []
    for _ in range(int(levels)):
        m = k.sma_nb(m, int(length))
        mas.append(m)
    stack = np.stack(mas)
    rng = k.highest_nb(close, int(hhll_length)) - k.lowest_nb(close, int(hhll_length))
    rbo = safe_div(100 * (close - stack.mean(axis=0)), rng)
    rb = safe_div(100 * (stack.max(axis=0) - stack.min(axis=0)), rng)
    return rbo, rb


@njit(cache=True)
def _is_prime(m):
    if m < 2:
        return False
    if m % 2 == 0:
        return m == 2
    r = int(math.sqrt(m))
    d = 3
    while d <= r:
        if m % d == 0:
            return False
        d += 2
    return True


@njit(cache=True)
def _prime_near(m, limit, step):
    """First prime from integer ``m`` in direction ``step`` within ``limit``."""
    j = m
    while (j <= limit) if step > 0 else (j >= limit):
        if _is_prime(j):
            return float(j)
        j += step
    return NAN


@njit(cache=True)
def _pine_prime(price, pct, step):
    """HPotter's literal Pine loop: ``for j = price to price +/- price*pct/100``
    with float ``j`` and divisors ``2 .. sqrt(price)``. Returns res1/res2."""
    lim = price + step * price * pct / 100.0
    sq = math.sqrt(price)
    res = 0.0
    j = price
    while (j <= lim) if step > 0 else (j >= lim):
        res = j
        i = 2.0
        if sq >= 2.0:
            while i <= sq:
                res = 0.0 if np.fmod(j, i) == 0 else j
                if res == 0:
                    break
                i += 1.0
        else:
            while i >= sq:
                res = 0.0 if np.fmod(j, i) == 0 else j
                if res == 0:
                    break
                i -= 1.0
        if res > 0:
            break
        j += step
    return res


@njit(cache=True)
def _pno_nb(x, pct, scale, hp):
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        prev = NAN
        for i in range(x.shape[0]):
            p = x[i, c]
            if np.isnan(p):
                out[i, c] = NAN if hp else prev
                prev = out[i, c]
                continue
            if hp:
                up = _pine_prime(p, pct, 1.0)
                dn = _pine_prime(p, pct, -1.0)
                res = up - p if up - p < p - dn else dn - p
                if res == 0:
                    res = prev
            else:
                m = int(math.floor(p * scale + 0.5))
                up = _prime_near(m, int(math.floor(m * (1 + pct / 100.0))), 1)
                dn = _prime_near(m, int(math.ceil(m * (1 - pct / 100.0))), -1)
                q = p * scale
                if np.isnan(up) and np.isnan(dn):
                    res = prev
                elif np.isnan(dn) or (not np.isnan(up) and up - q < q - dn):
                    res = (up - q) / scale
                else:
                    res = (dn - q) / scale
            out[i, c] = res
            prev = res
    return out


@njit(cache=True)
def _pnb_nb(x, pct, scale, step, hp):
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        prev = NAN
        for i in range(x.shape[0]):
            p = x[i, c]
            if np.isnan(p):
                out[i, c] = prev
                continue
            if hp:
                r = _pine_prime(p, pct, step)
                res = prev if r == 0 else r
            else:
                m = int(math.floor(p * scale + 0.5))
                lim = int(math.floor(m * (1 + pct / 100.0))) if step > 0 else int(math.ceil(m * (1 - pct / 100.0)))
                r = _prime_near(m, lim, 1 if step > 0 else -1)
                res = prev if np.isnan(r) else r / scale
            out[i, c] = res
            prev = res
    return out


@indicator("PRIME_NUMBER_OSC", ["close"], ["pno"])
def prime_number_oscillator(close, percent=5.0, scale=1.0, hpotter=False):
    """Prime Number Oscillator: distance from the price to the nearest prime
    (the one above when it is strictly closer, otherwise the one below).

    Primes are searched among integers, so the price is first scaled by
    ``scale`` (e.g. 100 for cents) and rounded; the search stops
    ``percent`` % away (no prime found: previous value).

    ``hpotter=True`` reproduces HPotter's Pine loop literally. It steps a
    *float* counter from the raw price, so on prices with decimals no
    candidate is ever divisible, both "primes" equal the price, and the
    oscillator never leaves na (his ``res == 0 ? res[1]`` hold) - the
    strategy's filter never fires. It only works on integer prices.
    """
    return _pno_nb(close, float(percent), float(scale), bool(hpotter))


@indicator("PRIME_NUMBER_BANDS", ["high", "low"], ["upper", "lower"])
def prime_number_bands(high, low, percent=5.0, scale=1.0, hpotter=False):
    """Prime Number Bands: nearest prime at or above the high (upper) and at
    or below the low (lower), searched ``percent`` % away (else hold).

    ``hpotter=True`` is HPotter's literal Pine loop; on prices with
    decimals it returns the high and low themselves (see
    :func:`prime_number_oscillator`), so his PNB strategy degenerates into
    a 5-bar high/low breakout.
    """
    s = float(scale)
    return (_pnb_nb(high, float(percent), s, 1.0, bool(hpotter)),
            _pnb_nb(low, float(percent), s, -1.0, bool(hpotter)))


# ---------------------------------------------------------------------------
# Katsanos Finite Volume Elements (TASC Apr 2003 / Sep 2003)
# ---------------------------------------------------------------------------

def _fve_mf(high, low, close):
    tp = (high + low + close) / 3
    return close - (high + low) / 2 + tp - shift_2d(tp, 1)


@indicator("FVE", ["high", "low", "close", "volume"], ["fve"])
def finite_volume_elements(high, low, close, volume, period=22, factor=0.3, hpotter=False):
    """Markos Katsanos' Finite Volume Elements (TASC Apr 2003).

    MF = close - hl2 + hlc3 - hlc3[1]; volume counts +V when MF >
    factor % of close, -V when MF < -factor %, else 0;
    FVE = sum(signed V, period) / sma(V, period) / period * 100.

    HPotter's FVE (``hpotter=True``) adds ``signed V / sma(V) / period * 100``
    to a running total forever (``nRes[1] + ...``) instead of summing the
    last ``period`` bars, so it drifts without bound: that is a bug, kept
    only for reproduction.
    """
    n = int(period)
    mf = _fve_mf(high, low, close)
    with np.errstate(invalid="ignore"):
        sv = np.where(mf > factor * close / 100, volume, np.where(mf < -factor * close / 100, -volume, 0.0))
    smav = k.sma_nb(volume, n)
    if hpotter:
        return _nzcum_nb(sv / smav / n * 100, 0.0)
    return safe_div(k.sum_nb(sv, n), smav) / n * 100


@indicator("VOLATILITY_FVE", ["high", "low", "close", "volume"], ["fve", "signal", "cutoff"])
def volatility_fve(high, low, close, volume, samples=22, perma=40, cintra=0.1, cinter=0.1, hpotter=False):
    """Katsanos' volatility-adjusted FVE (TASC Sep 2003).

    CutOff = cintra * stdev(log(H/L), samples) + cinter * stdev(log(TP/TP[1]),
    samples); volume is signed when MF exceeds +/- CutOff * close;
    FVE = 100 * sum(signed V) / sum(V) over ``samples``; signal = EMA(perma).

    ``hpotter=True`` uses HPotter's cutoff, stdev(sma(x, samples), samples)
    - the deviation of a moving average instead of the price-change
    volatility, which makes the cutoff far too small (bug).
    """
    n = int(samples)
    with np.errstate(divide="ignore", invalid="ignore"):
        intra = np.log(high) - np.log(low)
        tp = (high + low + close) / 3
        inter = np.log(tp) - np.log(shift_2d(tp, 1))
    if hpotter:
        intra, inter = k.sma_nb(intra, n), k.sma_nb(inter, n)
    cut = cintra * k.stdev_nb(intra, n) + cinter * k.stdev_nb(inter, n)
    mf = _fve_mf(high, low, close)
    with np.errstate(invalid="ignore"):
        f = np.where(mf > cut * close, 1.0, np.where(mf < -cut * close, -1.0, 0.0))
    fve = safe_div(k.sum_nb(volume * f, n), k.sum_nb(volume, n)) * 100
    return fve, k.ema_nb(fve, int(perma)), cut


# ---------------------------------------------------------------------------
# Volume indicators
# ---------------------------------------------------------------------------

@indicator("MODIFIED_PVT", ["open", "high", "low", "close", "volume"], ["mpvt", "signal"])
def modified_pvt(open, high, low, close, volume, level=1.0, scale=1.0, length=23, volume_divisor=50000.0):
    """Modified Price-Volume Trend (HPotter, after the TASC article): the PVT
    of ohlc4 with volume scaled by ``volume_divisor``:
    level + scale * cum(V / divisor * change(ohlc4) / ohlc4[1]); signal =
    sma(length). Starts on bar 1 (bar 0 has no change), like Pine's nz()."""
    x = (open + high + low + close) / 4
    term = volume / volume_divisor * safe_div(change_2d(x), shift_2d(x, 1))
    term[np.isnan(change_2d(x))] = NAN
    cum = _nzcum_nb(term, 0.0)
    res = level + scale * cum
    return res, k.sma_nb(res, int(length))


@njit(cache=True)
def _vol_index_add_nb(roc, volume, negative):
    out = np.full(roc.shape, NAN)
    for c in range(roc.shape[1]):
        prev = NAN
        for i in range(roc.shape[0]):
            p = 0.0 if np.isnan(prev) else prev
            hit = False
            if i > 0:
                dv = volume[i, c] - volume[i - 1, c]
                hit = (dv < 0) if negative else (dv > 0)
            v = p + roc[i, c] if hit else p
            out[i, c] = v
            prev = v
    return out


@njit(cache=True)
def _vol_index_mul_nb(close, volume, negative, start):
    out = np.full(close.shape, NAN)
    for c in range(close.shape[1]):
        v = start
        out[0, c] = v
        for i in range(1, close.shape[0]):
            dv = volume[i, c] - volume[i - 1, c]
            if ((dv < 0) if negative else (dv > 0)) and close[i - 1, c] != 0:
                v = v * close[i, c] / close[i - 1, c]
            out[i, c] = v
    return out


@indicator("VOLUME_INDEX", ["close", "volume"], ["index", "signal"])
def volume_index(close, volume, negative=False, signal_length=255, roc_length=1, start=1000.0, hpotter=False):
    """Fosback's Positive (``negative=False``) / Negative Volume Index.

    The index changes by the bar's percentage price change on bars where
    volume rises (PVI) or falls (NVI), compounding from ``start``; signal
    = EMA(255). Same numbers as ``tv_indicators.pvi`` / ``nvi``.

    ``hpotter=True`` is HPotter's additive version: a running sum of
    ``roc(close, roc_length)`` (in %) on those bars, starting at 0. His NVI
    combo strategy passes ``roc_length = EMA_Len`` (50), which sums 50-bar
    ROCs and is a bug.
    """
    if hpotter:
        v = _vol_index_add_nb(safe_div(change_2d(close, int(roc_length)), shift_2d(close, int(roc_length))) * 100,
                              volume, bool(negative))
    else:
        v = _vol_index_mul_nb(close, volume, bool(negative), float(start))
    return v, k.ema_nb(v, int(signal_length))


@indicator("EMA_VOLUME_WEIGHTED", ["close", "volume"], ["ema_vw"])
def ema_volume_weighted(close, volume, length=22):
    """Exponential volume-weighted average: ema(volume * close) / ema(volume)
    ("Combining Exponential And Volume Weighting", HPotter's port)."""
    n = int(length)
    return safe_div(k.ema_nb(volume * close, n), k.ema_nb(volume, n))


@njit(cache=True)
def _klinger_vf_nb(high, low, close, volume):
    out = np.full(close.shape, NAN)
    for c in range(close.shape[1]):
        tp_prev = NAN
        tr_prev = 0.0
        dm_prev = NAN
        cm = NAN
        for i in range(close.shape[0]):
            tp = high[i, c] + low[i, c] + close[i, c]
            trend = 1.0 if tp > tp_prev else -1.0
            dm = high[i, c] - low[i, c]
            if np.isnan(cm) or np.isnan(dm_prev):
                cm = dm
            elif trend == tr_prev:
                cm = cm + dm
            else:
                cm = dm_prev + dm
            temp = 2.0 if cm == 0 else abs(2.0 * (dm / cm - 1.0))
            out[i, c] = volume[i, c] * temp * trend * 100.0
            tp_prev = tp
            tr_prev = trend
            dm_prev = dm
    return out


@indicator("KLINGER_VO", ["high", "low", "close", "volume"], ["kvo", "signal"])
def klinger_volume_oscillator(high, low, close, volume, fast=34, slow=55, signal=13, hpotter=False):
    """Stephen Klinger's Volume Oscillator with his Volume Force
    (TASC Dec 1997): trend = sign of change(H+L+C); dm = H-L; cm accumulates
    dm while the trend holds (resets to dm[1] + dm on a flip);
    VF = V * |2 * (dm/cm - 1)| * trend * 100; KVO = EMA34(VF) - EMA55(VF),
    signal EMA13.

    ``hpotter=True`` is HPotter's simplified force, +/-100 * V by the sign of
    change(hlc3) (a tie counts as negative). TradingView's built-in
    (``tv_indicators.klinger``) is the same simplification without the x100
    and with ties counted as positive.
    """
    if hpotter:
        tp = (high + low + close) / 3
        vf = np.where(_gt(tp, shift_2d(tp, 1)), volume * 100, -volume * 100)
    else:
        vf = _klinger_vf_nb(high, low, close, volume)
    kvo = k.ema_nb(vf, int(fast)) - k.ema_nb(vf, int(slow))
    return kvo, k.ema_nb(kvo, int(signal))


@indicator("TFS_VOLUME_OSC", ["open", "close", "volume"], ["vo"])
def tfs_volume_oscillator(open, close, volume, length=7):
    """TFS Volume Oscillator (Strain & Whitley's TFS system, 2nd component):
    the ``length``-bar average of volume signed by the bar's direction
    (close > open +V, close < open -V, else 0)."""
    with np.errstate(invalid="ignore"):
        sv = np.where(close > open, volume, np.where(close < open, -volume, 0.0))
    return k.sum_nb(sv, int(length)) / int(length)


@indicator("HPOTTER_MONEY_FLOW", ["open", "high", "low", "close", "volume"], ["mf"])
def hpotter_money_flow(open, high, low, close, volume, fast=3, slow=10):
    """HPotter's "Money Flow Indicator (Chaikin Oscillator)": with
    f = (close - open) / (high - low) * volume (0 when the range or volume
    is 0), mf = ema(sum(f, slow), slow) - ema(sum(f, fast), fast).

    This is not Chaikin's oscillator (EMA3 - EMA10 of the cumulative A/D
    line, ``tv_indicators.chaikin_osc``): it uses Williams' close-open
    numerator and rolling sums. Kept as HPotter wrote it."""
    lmax, lmin = max(int(fast), int(slow)), min(int(fast), int(slow))
    with np.errstate(invalid="ignore", divide="ignore"):
        f = np.where((high - low) * volume > 0, (close - open) / (high - low) * volume, 0.0)
    return k.ema_nb(k.sum_nb(f, lmax), lmax) - k.ema_nb(k.sum_nb(f, lmin), lmin)


# ---------------------------------------------------------------------------
# M.H. Pee: Trend Continuation Factor, Trend Intensity Index
# ---------------------------------------------------------------------------

@njit(cache=True)
def _cf_nb(x):
    out = np.zeros(x.shape)
    for c in range(x.shape[1]):
        cf = 0.0
        for i in range(x.shape[0]):
            v = x[i, c]
            cf = 0.0 if v == 0 else v + cf
            out[i, c] = cf
    return out


@indicator("TCF", ["close"], ["plus_tcf", "minus_tcf"])
def trend_continuation_factor(close, length=35):
    """M.H. Pee's Trend Continuation Factor (TASC Mar 2002).

    +CF accumulates consecutive positive changes (0 on a non-up bar), -CF
    the negative ones; +TCF = sum(+change - -CF, n), -TCF = sum(-change -
    +CF, n). HPotter's port matches bar for bar (his ``nz(CF[1], 1)`` seed
    is never used because bar 0 has no change).
    """
    ch = change_2d(close)
    with np.errstate(invalid="ignore"):
        pc = np.where(ch > 0, ch, 0.0)
        mc = np.where(ch < 0, -ch, 0.0)
    pcf, mcf = _cf_nb(pc), _cf_nb(mc)
    n = int(length)
    return k.sum_nb(pc - mcf, n), k.sum_nb(mc - pcf, n)


@indicator("TII", ["close"], ["tii"])
def trend_intensity_index(close, major_length=60, minor_length=30):
    """M.H. Pee's Trend Intensity Index (TASC Jun 2002): over the last
    ``minor_length`` bars, 100 * sum of (close - SMA60) on bars above the SMA /
    sum of |close - SMA60|. NaN until all deviations exist (the TV ports
    replace missing values with 0, which only changes the warm-up)."""
    dev = close - k.sma_nb(close, int(major_length))
    with np.errstate(invalid="ignore"):
        pos = np.where(np.isnan(dev), NAN, np.where(dev > 0, dev, 0.0))
        neg = np.where(np.isnan(dev), NAN, np.where(dev > 0, 0.0, -dev))
    n = int(minor_length)
    sp, sn = k.sum_nb(pos, n), k.sum_nb(neg, n)
    return safe_div(100 * sp, sp + sn)


# ---------------------------------------------------------------------------
# Siligardos: Reverse Engineering RSI, Pivot Detector Oscillator
# ---------------------------------------------------------------------------

@njit(cache=True)
def _rersi_hp_nb(close, kk):
    auc = np.full(close.shape, NAN)
    adc = np.full(close.shape, NAN)
    for c in range(close.shape[1]):
        pu = NAN
        pd = NAN
        for i in range(close.shape[0]):
            c1 = close[i - 1, c] if i > 0 else NAN
            cl = close[i, c]
            u1 = 1.0 if np.isnan(pu) else pu
            d1 = 1.0 if np.isnan(pd) else pd
            if cl > c1:
                u = kk * (cl - c1) + (1 - kk) * u1
                d = (1 - kk) * d1
            else:
                u = (1 - kk) * u1
                d = kk * (c1 - cl) + (1 - kk) * d1
            auc[i, c] = u
            adc[i, c] = d
            pu, pd = u, d
    return auc, adc


@indicator("REVERSE_ENGINEERING_RSI", ["close"], ["price"])
def reverse_engineering_rsi(close, rsi_value=50.0, wilder_length=14, hpotter=False):
    """Giorgos Siligardos' Reverse Engineering RSI (TASC Jun 2003): the close
    needed on the next bar for Wilder's RSI(``wilder_length``) to reach
    ``rsi_value``. AUC/ADC are EMAs of up/down closes with period 2k-1;
    x = (k-1) * (ADC * v / (100 - v) - AUC); price = close + x when x >= 0,
    else close + x * (100 - v) / v.

    ``hpotter=True`` seeds AUC/ADC with 1 (``nz(AUC[1], 1)``) instead of an
    SMA; that only changes the warm-up.
    """
    kw = int(wilder_length)
    ep = 2 * kw - 1
    if hpotter:
        auc, adc = _rersi_hp_nb(close, 2.0 / (ep + 1))
    else:
        ch = change_2d(close)
        with np.errstate(invalid="ignore"):
            up = np.where(np.isnan(ch), NAN, np.where(ch > 0, ch, 0.0))
            dn = np.where(np.isnan(ch), NAN, np.where(ch > 0, 0.0, -ch))
        auc, adc = k.ema_nb(up, ep), k.ema_nb(dn, ep)
    v = float(rsi_value)
    x = (kw - 1) * (adc * v / (100 - v) - auc)
    with np.errstate(invalid="ignore"):
        return np.where(x >= 0, close + x, close + x * (100 - v) / v)


@indicator("PIVOT_DETECTOR_OSC", ["close"], ["pdo"])
def pivot_detector_oscillator(close, ma_length=200, rsi_length=14, up_entry=35.0, up_exit=85.0,
                              down_entry=20.0, down_exit=70.0):
    """Siligardos' Pivot Detector Oscillator (TASC Jul 2009): RSI(14)
    rescaled to 0..100 from 35..85 when close > SMA(200) and from 20..70
    otherwise. HPotter's port is faithful (he returns 0 instead of na while
    the 200-bar SMA warms up)."""
    ma = k.sma_nb(close, int(ma_length))
    r = rsi_2d(close, int(rsi_length))
    with np.errstate(invalid="ignore"):
        out = np.where(close > ma, (r - up_entry) / (up_exit - up_entry),
                       (r - down_entry) / (down_exit - down_entry)) * 100
    out[np.isnan(ma)] = NAN
    return out


# ---------------------------------------------------------------------------
# Dorsey: Relative Volatility Index, Inertia
# ---------------------------------------------------------------------------

def _rvi_dorsey(x, n, smooth, hpotter):
    sd = k.stdev_nb(x, n)
    ch = change_2d(x)
    if hpotter:
        u = np.where(_gt(x, shift_2d(x, 1)), sd, 0.0)
        d = np.where(_gt(x, shift_2d(x, 1)), 0.0, sd)
        nu = _wilder_nz_nb(u, float(smooth), 0.0)
        nd = _wilder_nz_nb(d, float(smooth), 0.0)
        with np.errstate(divide="ignore", invalid="ignore"):
            return 100 * nu / (nu + nd)
    bad = np.isnan(ch) | np.isnan(sd)
    with np.errstate(invalid="ignore"):
        u = np.where(bad, NAN, np.where(ch > 0, sd, 0.0))
        d = np.where(bad, NAN, np.where(ch < 0, sd, 0.0))
    nu, nd = k.rma_nb(u, int(smooth)), k.rma_nb(d, int(smooth))
    return safe_div(100 * nu, nu + nd)


@indicator("RVI_DORSEY", ["close"], ["rvi"])
def rvi_dorsey(close, stdev_length=10, smooth=14, hpotter=False):
    """Donald Dorsey's Relative Volatility Index (TASC Jun 1993): RSI built
    from the 10-bar standard deviation, put in the "up" leg on up closes and
    the "down" leg on down closes, each smoothed with Wilder's average (14).
    An unchanged close feeds neither leg (as in TA-Lib).

    ``hpotter=True``: HPotter's ``(13 * nz(nU[1]) + u) / 14`` (zero seed)
    and unchanged closes counted as down. TradingView's built-in
    (``tv_indicators.relative_volatility_index``) uses EMA(14) instead.
    """
    return _rvi_dorsey(close, int(stdev_length), int(smooth), bool(hpotter))


@indicator("INERTIA", ["high", "low", "close"], ["inertia"])
def inertia(high, low, close, stdev_length=10, smooth=14, linreg_length=20, ema_length=14, hpotter=False):
    """Dorsey's Inertia (TASC Sep 1995, "Refining the Relative Volatility
    Index"): the 20-bar linear-regression value of the refined RVI, the
    average of the RVI of highs and the RVI of lows.

    ``hpotter=True`` is HPotter's Inertia: ema(RVI of closes (his zero-seeded
    Wilder form), ``ema_length``). That replaces both the refined RVI and
    the regression, so it is a different (smoother, laggier) line.
    """
    if hpotter:
        return k.ema_nb(_rvi_dorsey(close, int(stdev_length), int(smooth), True), int(ema_length))
    r = (_rvi_dorsey(high, int(stdev_length), int(smooth), False)
         + _rvi_dorsey(low, int(stdev_length), int(smooth), False)) / 2
    return k.linreg_nb(r, int(linreg_length), 0)


# ---------------------------------------------------------------------------
# Blau's ergodic family (Momentum, Direction, and Divergence, 1995)
# ---------------------------------------------------------------------------

def _e3(x, r, s, u):
    out = k.ema_nb(x, int(r))
    if int(s) > 1:
        out = k.ema_nb(out, int(s))
    if int(u) > 1:
        out = k.ema_nb(out, int(u))
    return out


def _ratio0(num, den):
    """num / den with 0 where den == 0 (HPotter's ``Val2 != 0 ? ... : 0``)."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(den == 0, 0.0, num / den)


@indicator("ERGODIC_TSI", ["close"], ["tsi", "signal"])
def ergodic_tsi(close, r=25, s=13, u=1, signal_length=5):
    """Blau's True Strength Index TSI(r, s, u) =
    100 * E_u(E_s(E_r(mtm))) / E_u(E_s(E_r(|mtm|))) with mtm = change(close),
    and the Ergodic signal line EMA(signal_length). u=1 is the classic
    double-smoothed TSI (``tv_indicators.tsi``); HPotter's Ergodic TSI uses
    (4, 8, 6, 3). A zero denominator gives 0, as in his port."""
    m = change_2d(close)
    t = _ratio0(100 * _e3(m, r, s, u), _e3(np.abs(m), r, s, u))
    return t, k.ema_nb(t, int(signal_length))


@indicator("ERGODIC_MDI", ["close"], ["mdi", "signal"])
def ergodic_mdi(close, r=32, s=5, u=5, signal_length=5):
    """Blau's Ergodic Mean Deviation Indicator: MDI = E_u(E_s(close -
    EMA_r(close))), signal = EMA(MDI, signal_length). HPotter takes the
    signal length from ``u`` and ignores his SmthLen input; with his
    defaults (u = 5) that equals signal_length = 5."""
    mdi = _e3(close - k.ema_nb(close, int(r)), s, u, 1)
    return mdi, k.ema_nb(mdi, int(signal_length))


@indicator("ERGODIC_CSI", ["open", "high", "low", "close"], ["csi", "signal"])
def ergodic_candlestick_oscillator(open, high, low, close, r=32, s=12, u=1, q=1, signal_length=5):
    """Blau's Candlestick Index CSI(q, r, s, u) and its Ergodic signal:
    100 * E_u(E_s(E_r(close - open[q-1]))) / E_u(E_s(E_r(HHV(high, q) -
    LLV(low, q)))). With q = 1, u = 1 this is the Ergodic Candlestick
    Oscillator (ECO) of HPotter's ECO strategy (32, 12); Blau's "Ergodic CSI"
    is the same index (MQL5 defaults q=1, r=20, s=5, u=3, signal 3).

    HPotter's "Ergodic CSI" strategies compute something else: Wilder's
    Commodity Selection Index (ADX(1) x ATR(1)) / close smoothed by an SMA.
    """
    qq = int(q)
    mom = close - shift_2d(open, qq - 1)
    rng = k.highest_nb(high, qq) - k.lowest_nb(low, qq)
    csi = _ratio0(100 * _e3(mom, r, s, u), _e3(rng, r, s, u))
    return csi, k.ema_nb(csi, int(signal_length))


@indicator("DTI_BLAU", ["high", "low"], ["dti"])
def directional_trend_index(high, low, r=14, s=10, u=5):
    """Blau's Directional Trend Index: HMU = max(high - high[1], 0), LMD =
    max(low[1] - low, 0); DTI = 100 * E_u(E_s(E_r(HMU - LMD))) /
    E_u(E_s(E_r(|HMU - LMD|))). HPotter's port is faithful."""
    dh = change_2d(high)
    dl = change_2d(low)
    with np.errstate(invalid="ignore"):
        hmu = np.where(dh > 0, dh, 0.0)
        lmd = np.where(dl < 0, -dl, 0.0)
    x = hmu - lmd
    return _ratio0(100 * _e3(x, r, s, u), _e3(np.abs(x), r, s, u))


# ---------------------------------------------------------------------------
# Stochastic / RSI variants
# ---------------------------------------------------------------------------

@indicator("DSS_BRESSERT", ["high", "low", "close"], ["dss", "signal"])
def dss_bressert(high, low, close, length=10, smooth=9, signal_length=5):
    """Walter Bressert's Double Smoothed Stochastic: EMA of the raw %K, then
    the stochastic of that EMA over ``length`` bars, smoothed again; signal =
    EMA(signal_length). HPotter's port is faithful (10, 9, 5)."""
    n, e = int(length), int(smooth)
    pre = k.ema_nb(stoch_2d(close, high, low, n), e)
    dss = k.ema_nb(stoch_2d(pre, pre, pre, n), e)
    return dss, k.ema_nb(dss, int(signal_length))


@indicator("HPOTTER_OBOS", ["high", "low", "close"], ["obos"])
def hpotter_obos(high, low, close, length=10):
    """HPotter's Overbought/Oversold: stoch(length) / 100 when close >
    close[length], else (100 - stoch) / 100."""
    n = int(length)
    st = stoch_2d(close, high, low, n)
    return np.where(_gt(close, shift_2d(close, n)), st / 100, (100 - st) / 100)


@indicator("EHLERS_SMOOTHED_RSI", ["close"], ["rsi"])
def ehlers_smoothed_rsi(close, length=10):
    """Ehlers' Smoothed RSI ("Cybernetic Analysis", 2004): RSI (0..1) of the
    4-bar FIR (c + 2c[1] + 2c[2] + c[3]) / 6 using plain sums over
    ``length`` bars; 0 when there is no movement. HPotter's port is faithful."""
    sm = (close + 2 * shift_2d(close, 1) + 2 * shift_2d(close, 2) + shift_2d(close, 3)) / 6
    d = change_2d(sm)
    with np.errstate(invalid="ignore"):
        cu = k.sum_nb(np.where(d > 0, d, 0.0), int(length))
        cd = k.sum_nb(np.where(d < 0, -d, 0.0), int(length))
    return _ratio0(cu, cu + cd)


@njit(cache=True)
def _dyn_rsi_nb(x, td):
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        up = NAN
        dn = NAN
        for i in range(1, x.shape[0]):
            t = td[i, c]
            ch = x[i, c] - x[i - 1, c]
            if np.isnan(t) or np.isnan(ch):
                continue
            g = ch if ch > 0 else 0.0
            l = -ch if ch < 0 else 0.0
            if np.isnan(up):
                n = int(t)
                if i < n:
                    continue
                su = 0.0
                sd = 0.0
                ok = True
                for j in range(n):
                    cj = x[i - j, c] - x[i - j - 1, c]
                    if np.isnan(cj):
                        ok = False
                        break
                    su += cj if cj > 0 else 0.0
                    sd += -cj if cj < 0 else 0.0
                if not ok:
                    continue
                up = su / n
                dn = sd / n
            else:
                up += (g - up) / t
                dn += (l - dn) / t
            if dn == 0:
                out[i, c] = 100.0
            elif up == 0:
                out[i, c] = 0.0
            else:
                out[i, c] = 100.0 - 100.0 / (1.0 + up / dn)
    return out


@indicator("DYNAMIC_MOMENTUM_INDEX", ["close"], ["dmi", "period"])
def dynamic_momentum_index(close, base_length=14, stdev_length=5, avg_length=10, min_length=5, max_length=30):
    """Chande & Kroll's Dynamic Momentum Index ("The New Technical Trader",
    1994): an RSI whose period adapts to volatility.

    Vi = stdev(close, 5) / sma(stdev(close, 5), 10); period =
    int(14 / Vi) clamped to 5..30; DMI = Wilder RSI of close where each
    bar's smoothing uses that bar's period (TradeStation ``RSI(C, Td)``),
    seeded with the simple average of the first ``period`` changes.

    HPotter's DMI computes ``round(14 / sma(stdev) - 0.5)`` (no ratio to the
    current stdev), clamps it, and then takes the RSI *of the period series*
    instead of an RSI of price with that period: a bug.
    """
    sd = k.stdev_nb(close, int(stdev_length))
    vi = safe_div(sd, k.sma_nb(sd, int(avg_length)))
    with np.errstate(divide="ignore", invalid="ignore"):
        td = np.where(vi == 0, float(max_length), np.floor(base_length / vi))
    td = np.clip(td, min_length, max_length)
    return _dyn_rsi_nb(close, np.ascontiguousarray(td)), td


@indicator("CMO_AVERAGE", ["close"], ["cmo_av"])
def cmo_average(close, length1=5, length2=10, length3=20, absolute=False):
    """CMOav: the average of Chande's CMO at three lengths (each 100 *
    sum(mom) / sum(|mom|), the TradingView ``ta.cmo``). ``absolute=True`` is
    HPotter's CMOabsav, |CMOav|."""
    out = 0.0
    for n in (int(length1), int(length2), int(length3)):
        m = change_2d(close)
        out = out + safe_div(k.sum_nb(m, n), k.sum_nb(np.abs(m), n))
    out = 100 * out / 3
    return np.abs(out) if absolute else out


@indicator("CMO_FILTERED", ["close"], ["cmo"])
def cmo_filtered(close, length=9, filter=3.0):
    """CMOfilt (Chande): CMO built only from bar changes larger than
    ``filter`` price units: 100 * sum(filtered mom) / sum(|filtered mom|).
    HPotter's port is faithful."""
    m = change_2d(close)
    with np.errstate(invalid="ignore"):
        keep = np.abs(m) > filter
    fm = np.where(keep, m, 0.0)
    return safe_div(100 * k.sum_nb(fm, int(length)), k.sum_nb(np.abs(fm), int(length)))


@indicator("CMO_DISPARITY", ["close"], ["first", "second", "third"])
def cmo_disparity(close, length1=50, length2=25, length3=10, hpotter=False):
    """Disparity index on three EMAs, as in HPotter's "CMOaDisparity Index":
    100 * (close - EMA) / EMA (Nison's disparity). ``hpotter=True`` divides
    by close instead of the EMA, as HPotter does (a different scale)."""
    outs = []
    for n in (int(length1), int(length2), int(length3)):
        e = k.ema_nb(close, n)
        outs.append(safe_div(100 * (close - e), close if hpotter else e))
    return tuple(outs)


@indicator("RAVI", ["close"], ["ravi"])
def ravi(close, fast=7, slow=65, hpotter=False):
    """Chande's Range Action Verification Index ("Beyond Technical Analysis"):
    |100 * (SMA7 - SMA65) / SMA65| - a trend-strength measure without
    direction. ``hpotter=True`` keeps the sign, as in HPotter's port."""
    s = k.sma_nb(close, int(slow))
    r = safe_div(100 * (k.sma_nb(close, int(fast)) - s), s)
    return r if hpotter else np.abs(r)


@indicator("PFE", ["close"], ["pfe", "raw"])
def polarized_fractal_efficiency(close, length=10, smooth=5, hpotter=False):
    """Hans Hannula's Polarized Fractal Efficiency (TASC Jan 1994):
    over ``length`` bars (``length - 1`` steps), 100 * sqrt(change^2 +
    length^2) / sum(sqrt(step^2 + 1)), negative when the close is not above
    the first close; smoothed with EMA(``smooth``). (Hannula's MetaStock code:
    Roc(C, 9, $), Pwr(10, 2), Sum(..., 9) for length 10.)

    ``hpotter=True``: HPotter's port with ``length`` as the lag (his default
    9 = Hannula's 10-bar window), the horizontal term hard-coded to 100
    (correct only for his default) and the ratio rounded to an integer.
    """
    n = int(length)
    lag = n if hpotter else n - 1
    horiz2 = 100.0 if hpotter else float(n * n)
    d = change_2d(close, lag)
    num = np.sqrt(d * d + horiz2)
    den = k.sum_nb(np.sqrt(change_2d(close) ** 2 + 1), lag)
    r = safe_div(num, den) * 100
    if hpotter:
        r = _pine_round(r)
    raw = np.where(_gt(d, 0), r, -r)
    return k.ema_nb(raw, int(smooth)), raw


@indicator("CONFLUENCE", ["open", "high", "low", "close"], ["confluence"])
def confluence(open, high, low, close, harmonic=10):
    """The "Confluence" indicator (TradeStation, ported by HPotter): it
    combines momentum, error and trend-cycle scores of four moving averages
    whose lengths double from ``harmonic`` (10, 19, 37, 73) into a -9..9
    reading. A faithful vectorised copy of HPotter's code."""
    price = close
    def rnd(x):
        return int(math.floor(x + 0.5))
    H = int(harmonic)
    STL = rnd(H * 2 - 1 - 0.5)
    ITL = rnd(STL * 2 - 1 - 0.5)
    LTL = rnd(ITL * 2 - 1 - 0.5)
    HOFF = rnd(H / 2 - 0.5)
    SOFF = rnd(STL / 2 - 0.5)
    IOFF = rnd(ITL / 2 - 0.5)
    sma = k.sma_nb
    sh = shift_2d
    havg, savg, iavg, lavg = sma(price, H), sma(price, STL), sma(price, ITL), sma(price, LTL)
    momsig = (savg - sh(havg, HOFF)) + (iavg - sh(savg, SOFF)) + (lavg - sh(iavg, IOFF))
    lavg_ohlc = sma((open + high + low + close) / 4, LTL - 1)
    h2, s2, i2 = sma(price, H - 1), sma(price, STL - 1), sma(price, ITL - 1)
    l2 = sma(price, LTL - 1)

    def val(avg, a2, n, sum_src):
        deriv = avg * 2 - sh(avg, 1)
        dr = n * deriv - a2 * (n - 1)
        return (sum_src * (n - 1) + dr) / n

    v5 = val(havg, h2, H, h2)
    v6 = val(savg, s2, STL, s2)
    v7 = val(iavg, i2, ITL, i2)
    v13 = val(lavg, l2, LTL, lavg_ohlc)
    mom = (v6 - sh(v5, HOFF)) + (v7 - sh(v6, SOFF)) + (v13 - sh(v7, IOFF))

    def sc(x):
        return np.sin(x * 2 * 3.14 / 360) + np.cos(x * 2 * 3.14 / 360)

    xsum = sc(v5) + sc(v6) + sc(v7)
    xerr = sc(havg) + sc(savg) + sc(iavg)
    with np.errstate(invalid="ignore"):
        cond2 = (((xsum > sh(xsum, SOFF)) & (havg < sh(havg, SOFF)))
                 | ((xsum < sh(xsum, SOFF)) & (havg > sh(havg, SOFF))))
    phase = np.where(cond2, -1.0, 1.0)
    errsum = (xsum - xerr) * phase
    errsig = sma(errsum, SOFF)
    v70 = v5 - v13
    v71 = sma(v70, H)

    def score(x, sig):
        x1 = sh(x, 1)
        with np.errstate(invalid="ignore"):
            return np.select(
                [(x > 0) & (x < x1) & (x < sig), (x > 0) & (x < x1) & (x > sig),
                 (x > 0) & (x > x1) & (x < sig), (x > 0) & (x > x1) & (x > sig),
                 (x < 0) & (x > x1) & (x > sig), (x < 0) & (x < x1) & (x > sig),
                 (x < 0) & (x > x1) & (x < sig), (x < 0) & (x < x1) & (x < sig)],
                [1.0, 2.0, 2.0, 3.0, -1.0, -2.0, -2.0, -3.0], 0.0)

    v42 = score(errsum, errsig) + score(mom, momsig) + score(v70, v71)
    with np.errstate(invalid="ignore"):
        return np.select([(v42 > 0) & (v70 > 0), (v42 < 0) & (v70 < 0),
                          ((v42 > 0) & (v70 < 0)) | ((v42 < 0) & (v70 > 0))],
                         [v42, v42, v42 / 10], 0.0)


# ---------------------------------------------------------------------------
# Ehlers filters as HPotter ported them (bandpass, ETT, EMD, DSP, ELI, Fisher)
# ---------------------------------------------------------------------------

@njit(cache=True)
def _bandpass_nb(x, a0, b1, b2):
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        p1 = NAN
        p2 = NAN
        for i in range(x.shape[0]):
            d = x[i, c] - x[i - 2, c] if i >= 2 else NAN
            v = a0 * d + b1 * (0.0 if np.isnan(p1) else p1) - b2 * (0.0 if np.isnan(p2) else p2)
            out[i, c] = v
            p2 = p1
            p1 = v
    return out


def _bandpass(high, low, length, delta, pi):
    deg = pi / 180.0
    beta = math.cos(360.0 / length * deg)
    gamma = 1.0 / math.cos(720.0 * delta / length * deg)
    alpha = gamma - math.sqrt(gamma * gamma - 1)
    return _bandpass_nb((high + low) / 2, 0.5 * (1 - alpha), beta * (1 + alpha), alpha)


@indicator("EHLERS_BANDPASS_HL2", ["high", "low"], ["bp"])
def ehlers_bandpass(high, low, length=20, delta=0.5, hpotter=False):
    """Ehlers' bandpass filter of hl2 (Ehlers & Way, TASC Mar 2010):
    BP = 0.5 (1 - a)(p - p[2]) + b(1 + a) BP[1] - a BP[2] with b =
    cos(360/L), g = 1/cos(720 delta/L), a = g - sqrt(g^2 - 1); zero-seeded.
    ``hpotter=True`` converts degrees with pi = 3.14, as HPotter's Bandpass
    Filter strategies do (a slightly different filter)."""
    return _bandpass(high, low, float(length), float(delta), _PI_BANDPASS_HP if hpotter else math.pi)


@indicator("EXTRACTING_THE_TREND", ["high", "low"], ["trend", "bp"])
def extracting_the_trend(high, low, length=20, delta=0.5, hpotter=False):
    """Ehlers & Way's trend extraction (TASC Mar 2010): the 2*L-bar SMA of
    the bandpass output. ``hpotter=True`` uses HPotter's pi = 3.1415."""
    bp = _bandpass(high, low, float(length), float(delta), _PI_EMD_HP if hpotter else math.pi)
    return k.sma_nb(bp, 2 * int(length)), bp


@njit(cache=True)
def _peak_valley_nb(bp):
    pk = np.full(bp.shape, NAN)
    vl = np.full(bp.shape, NAN)
    for c in range(bp.shape[1]):
        p = NAN
        v = NAN
        for i in range(bp.shape[0]):
            pp = 0.0 if np.isnan(p) else p
            vv = 0.0 if np.isnan(v) else v
            if i >= 2:
                b0, b1, b2 = bp[i, c], bp[i - 1, c], bp[i - 2, c]
                if b1 > b0 and b1 > b2:
                    pp = b1
                if b1 < b0 and b1 < b2:
                    vv = b1
            pk[i, c] = pp
            vl[i, c] = vv
            p, v = pp, vv
    return pk, vl


@indicator("EMPIRICAL_MODE_DECOMP", ["high", "low"], ["mean", "peak", "valley"])
def empirical_mode_decomposition(high, low, length=20, delta=0.5, fraction=0.1, avg_length=50, hpotter=False):
    """Ehlers & Way's Empirical Mode Decomposition (TASC Mar 2010): mean =
    SMA(BP, 2L); peak/valley = ``fraction`` * SMA(last bandpass peak/valley,
    50). Trend up when mean > both lines. ``hpotter=True`` uses pi = 3.1415."""
    bp = _bandpass(high, low, float(length), float(delta), _PI_EMD_HP if hpotter else math.pi)
    pk, vl = _peak_valley_nb(bp)
    n = int(avg_length)
    return k.sma_nb(bp, 2 * int(length)), fraction * k.sma_nb(pk, n), fraction * k.sma_nb(vl, n)


@indicator("DSP", ["high", "low"], ["dsp"])
def detrended_synthetic_price(high, low, length=14):
    """Ehlers' Detrended Synthetic Price ("MESA and Trading Market Cycles"):
    EMA(hl2, L) - EMA(hl2, 2L), the quarter-cycle minus half-cycle EMA, with
    L a quarter of the dominant cycle. HPotter's D_DSP port is faithful."""
    hl2 = (high + low) / 2
    n = int(length)
    return k.ema_nb(hl2, n) - k.ema_nb(hl2, 2 * n)


@indicator("EHLERS_LEADING_INDICATOR", ["high", "low"], ["eli", "dsp"])
def ehlers_leading_indicator(high, low, length=7):
    """Ehlers Leading Indicator as in the D_ELI scripts: DSP - EMA(DSP, L).
    HPotter computes it on daily hl2 (``request.security(..., 'D', hl2)``);
    pass daily bars to reproduce that."""
    dsp = detrended_synthetic_price.core(high, low, length)
    return dsp - k.ema_nb(dsp, int(length)), dsp


@njit(cache=True)
def _fisher_hp_nb(src, hi, lo):
    fish_out = np.full(src.shape, NAN)
    trig_out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        pv = NAN
        pf = NAN
        for i in range(src.shape[0]):
            rng = hi[i, c] - lo[i, c]
            v = 0.33 * 2 * ((src[i, c] - lo[i, c]) / rng - 0.5) + 0.67 * (0.0 if np.isnan(pv) else pv) \
                if rng != 0 else NAN
            v2 = 0.999 if v > 0.99 else (-0.999 if v < -0.99 else v)
            f = 0.5 * math.log((1 + v2) / (1 - v2)) + 0.5 * (0.0 if np.isnan(pf) else pf) \
                if not np.isnan(v2) else NAN
            fish_out[i, c] = f
            trig_out[i, c] = pf
            pv = v
            pf = f
    return fish_out, trig_out


@indicator("FISHER_TRANSFORM", ["high", "low"], ["fisher", "trigger"])
def fisher_transform(high, low, length=10, hpotter=False):
    """Ehlers' Fisher Transform of hl2 ("Cybernetic Analysis", 2004): the
    normalised price is clamped to +/-0.999 *and fed back clamped* - the same
    as ``tv_indicators.fisher``.

    ``hpotter=True``: HPotter clamps only the copy that goes into the log
    and feeds the unclamped value back, so the recursion differs whenever
    |value| > 0.99.
    """
    src = (high + low) / 2
    n = int(length)
    hi, lo = k.highest_nb(src, n), k.lowest_nb(src, n)
    if hpotter:
        return _fisher_hp_nb(src, hi, lo)
    return k.fisher_nb(src, hi, lo)


# ---------------------------------------------------------------------------
# Moving averages and bands
# ---------------------------------------------------------------------------

@njit(cache=True)
def _kama_hp_nb(x, sc):
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        prev = NAN
        for i in range(x.shape[0]):
            p = 0.0 if np.isnan(prev) else prev
            v = p + sc[i, c] * (x[i, c] - p)
            out[i, c] = v
            prev = v
    return out


@indicator("KAMA_HP", ["close"], ["kama"])
def kama(close, length=10, fast=2, slow=30, hpotter=False):
    """Kaufman's Adaptive Moving Average (same numbers as
    ``tv_indicators.kama`` / TA-Lib). ``hpotter=True`` is HPotter's port:
    smoothing constants rounded to 0.666 / 0.0645 (fixed, whatever ``fast``
    and ``slow``), ER = 0 while its window is incomplete, and the average
    seeded at 0, so it needs a few hundred bars to converge."""
    n = int(length)
    if not hpotter:
        return k.kama_nb(close, n, float(fast), float(slow))
    noise = k.sum_nb(np.abs(change_2d(close)), n)
    with np.errstate(invalid="ignore", divide="ignore"):
        er = np.where(noise != 0, np.abs(change_2d(close, n)) / noise, 0.0)
    er[np.isnan(noise)] = 0.0
    sc = (er * (0.666 - 0.0645) + 0.0645) ** 2
    return _kama_hp_nb(close, np.ascontiguousarray(sc))


@indicator("RMTA", ["close"], ["rmta"])
def recursive_moving_trend_average(close, length=21):
    """Dennis Meyers' Recursive Moving Trend Average (TASC Dec 1998, "The
    Japanese Yen, Recursed"): alpha = 2/(n+1); Bot = (1-a) Bot[1] + close;
    RMTA = (1-a) RMTA[1] + a (close + Bot - Bot[1]); both seeded with the
    first close (Bot[1] = 0 on the first bar), exactly as HPotter's port."""
    a = 2.0 / (int(length) + 1)
    return _rmta_nb(close, a)


@njit(cache=True)
def _rmta_nb(x, a):
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        bot = NAN
        res = NAN
        for i in range(x.shape[0]):
            cl = x[i, c]
            b1 = cl if np.isnan(bot) else bot
            nb = (1 - a) * b1 + cl
            r1 = cl if np.isnan(res) else res
            nr = (1 - a) * r1 + a * (cl + nb - (0.0 if np.isnan(bot) else bot))
            bot, res = nb, nr
            out[i, c] = nr
    return out


@indicator("T3_CCI", ["close"], ["t3cci", "cci"])
def t3_cci(close, cci_length=14, t3_length=5, b=0.618):
    """FX Sniper's T3-CCI (MT4), ported by HPotter: a Tillson T3 of
    CCI(close, 14) built from six zero-seeded EMAs with weight 2/(nr+1),
    nr = 1 + 0.5 (n - 1). Faithful port."""
    n = int(cci_length)
    cci = safe_div(close - k.sma_nb(close, n), 0.015 * k.dev_nb(close, n))
    nn = max(int(t3_length), 1)
    w1 = 2.0 / (1 + 0.5 * (nn - 1) + 1)
    e1 = _ema_nz_nb(cci, w1)
    e2 = _ema_nz_nb(e1, w1)
    e3 = _ema_nz_nb(e2, w1)
    e4 = _ema_nz_nb(e3, w1)
    e5 = _ema_nz_nb(e4, w1)
    e6 = _ema_nz_nb(e5, w1)
    b2, b3 = b * b, b * b * b
    out = -b3 * e6 + 3 * (b2 + b3) * e5 - 3 * (2 * b2 + b + b3) * e4 + (1 + 3 * b + b3 + 3 * b2) * e3
    return out, cci


@indicator("KELTNER_ORIGINAL", ["high", "low", "close"], ["basis", "upper", "lower"])
def keltner_original(high, low, close, length=10, mult=1.0):
    """Chester Keltner's original channel ("How to Make Money in
    Commodities", 1960): SMA(hlc3, 10) +/- SMA(high - low, 10). HPotter's
    Keltner Channel port is this version (TradingView's built-in uses
    EMA/ATR)."""
    n = int(length)
    b = k.sma_nb((high + low + close) / 3, n)
    r = k.sma_nb(high - low, n) * mult
    return b, b + r, b - r


@indicator("HIGH_LOW_BANDS", ["close"], ["basis", "upper", "lower"])
def high_low_bands(close, length=14, percent=1.0, hpotter=False):
    """High Low Bands: a triangular MA shifted up and down by ``percent``.
    The triangular MA is MetaStock's / TA-Lib's (``tv_indicators.trima``).
    ``hpotter=True`` uses HPotter's sma(sma(close, n), n), a triangle twice
    as long."""
    n = int(length)
    if hpotter:
        t = k.sma_nb(k.sma_nb(close, n), n)
    else:
        t = k.sma_nb(k.sma_nb(close, (n + 1) // 2), n // 2 + 1)
    return t, t * (1 + percent / 100), t * (1 - percent / 100)


@indicator("MADE", ["close"], ["upper", "lower", "basis"])
def ma_displaced_envelope(close, length=9, percent_above=0.5, percent_below=0.5, displacement=13):
    """Moving Average Displaced Envelope: EMA(length) taken ``displacement``
    bars ago, +/- percent. Faithful to HPotter's MADE."""
    e = shift_2d(k.ema_nb(close, int(length)), int(displacement))
    return e * (100 + percent_above) / 100, e * (100 - percent_below) / 100, e


@indicator("APZ", ["high", "low", "close"], ["upper", "lower", "basis"])
def adaptive_price_zone(high, low, close, periods=20, band_pct=2.0):
    """Lee Leibfarth's Adaptive Price Zone (TASC Sep 2006): double EMA of
    close and of (high - low) with period ceil(sqrt(periods)); bands =
    basis +/- band_pct * smoothed range. HPotter's port is faithful."""
    p = int(math.ceil(math.sqrt(periods)))
    b = k.ema_nb(k.ema_nb(close, p), p)
    r = k.ema_nb(k.ema_nb(high - low, p), p)
    return b + band_pct * r, b - band_pct * r, b


@indicator("DAPD", ["high", "low"], ["dapd", "top", "bottom"])
def dapd_bands(high, low, length=21):
    """DAPD (Daily Average Price Delta) bands: dapd = SMA(high) - SMA(low);
    top = high + dapd, bottom = low - dapd (HPotter trades breaks of the
    previous bar's top/bottom)."""
    n = int(length)
    d = k.sma_nb(high, n) - k.sma_nb(low, n)
    return d, high + d, low - d


@indicator("BW_3LINES", ["high", "low"], ["jaw", "teeth", "lips"])
def bill_williams_3lines(high, low, jaw_length=13, teeth_length=8, lips_length=5,
                         jaw_offset=8, teeth_offset=5, lips_offset=3, hpotter=False):
    """Bill Williams' three averages (the Alligator): SMMA of hl2, displaced
    forward; the values are the ones drawn under the current bar (same as
    ``tv_indicators.alligator``). ``hpotter=True`` uses SMAs, as HPotter's
    "Bill Williams Averages. 3Lines"."""
    src = (high + low) / 2
    f = k.sma_nb if hpotter else k.rma_nb
    return (shift_2d(f(src, int(jaw_length)), int(jaw_offset)),
            shift_2d(f(src, int(teeth_length)), int(teeth_offset)),
            shift_2d(f(src, int(lips_length)), int(lips_offset)))


@indicator("HPOTTER_COG", ["close"], ["cog", "upper1", "lower1", "upper2", "lower2"])
def hpotter_center_of_gravity(close, length=20, offset=5, percent=1.0):
    """HPotter's "Center of Gravity" bands: linreg(close, length, offset)
    +/- 1x and 2x ``percent`` % of close. Not Ehlers' CG oscillator
    (``tv_indicators.center_of_gravity``)."""
    lg = k.linreg_nb(close, int(length), int(offset))
    d = close * percent / 100
    return lg, lg + d, lg - d, lg + 2 * d, lg - 2 * d


# ---------------------------------------------------------------------------
# Momentum / trend oscillators
# ---------------------------------------------------------------------------

def _roc(x, n):
    p = shift_2d(x, int(n))
    return safe_div(x - p, p) * 100


_SPECIAL_K = ((10, 10, 1), (15, 10, 2), (20, 10, 3), (30, 15, 4), (40, 50, 1), (65, 65, 2), (75, 75, 3),
              (100, 100, 4), (195, 130, 1), (265, 130, 2), (390, 130, 3), (530, 195, 4))


@indicator("PRING_SPECIAL_K", ["close"], ["special_k", "signal"])
def pring_special_k(close, smooth=10):
    """Martin Pring's Special K (daily): the sum of 12 smoothed ROCs
    weighted 1-4 (ROC 10..530, SMA 10..195), the short-, intermediate- and
    long-term KSTs combined; signal = SMA(smooth). HPotter's port is
    faithful."""
    out = 0.0
    for r, s, w in _SPECIAL_K:
        out = out + k.sma_nb(_roc(close, r), s) * w
    return out, k.sma_nb(out, int(smooth))


@indicator("FAST_SLOW_KURTOSIS", ["close"], ["kurtosis", "fast", "fast_slow"])
def fast_slow_kurtosis(close, length=65, wma_length=3):
    """Fast & Slow Kurtosis (MetaStock "Kurtosis"): K = mom(mom(close, 3), 1),
    FK = EMA(K, 65), FSK = WMA(FK, 3), as in HPotter's port."""
    kk = change_2d(change_2d(close, 3), 1)
    fk = k.ema_nb(kk, int(length))
    return kk, fk, k.wma_nb(fk, int(wma_length))


@indicator("STAT_VOLATILITY_EV", ["high", "low", "close"], ["sv"])
def statistical_volatility(high, low, close, length=30, annual=253):
    """Statistical volatility by the extreme-value method (Parkinson's
    0.6 * ln(range) estimator on the ``length``-bar close range and
    high-low range, annualised by sqrt(annual / length), averaged and
    clipped to 0..2.99). HPotter's port is faithful."""
    n = int(length)
    st = math.sqrt(annual / n)
    with np.errstate(divide="ignore", invalid="ignore"):
        v = (0.6 * np.log(k.highest_nb(close, n) / k.lowest_nb(close, n)) * st
             + 0.6 * np.log(k.highest_nb(high, n) / k.lowest_nb(low, n)) * st) * 0.5
    return np.where(np.isnan(v), NAN, np.clip(v, 0.0, 2.99))


@indicator("SIGNAL_TO_NOISE", ["close"], ["stn"])
def signal_to_noise(close, length=21):
    """HPotter's "Signal To Noise": -10 * ln(sum over i = 1..length-1 of
    (1 / close[i]) / length). (Note the sum skips the current bar and is
    still divided by ``length``.) Faithful copy."""
    n = int(length)
    s = shift_2d(k.sum_nb(1.0 / close, n - 1), 1) / n
    with np.errstate(divide="ignore", invalid="ignore"):
        return -10 * np.log(s)


@indicator("THREE_TEN_OSC", ["high", "low", "close"], ["osc", "signal"])
def three_ten_oscillator(high, low, close, fast=3, slow=10, signal=16, hpotter=False):
    """Linda Raschke's 3/10 oscillator ("Street Smarts"): SMA3 - SMA10 of
    close with a 16-bar SMA signal. ``hpotter=True``: HPotter's D_Three Ten
    Osc, EMA3 - EMA10 of hl2 (he computes it on daily bars)."""
    if hpotter:
        src = (high + low) / 2
        o = k.ema_nb(src, int(fast)) - k.ema_nb(src, int(slow))
    else:
        o = k.sma_nb(close, int(fast)) - k.sma_nb(close, int(slow))
    return o, k.sma_nb(o, int(signal))


@indicator("DINAPOLI_DETRENDED_OSC", ["close"], ["osc"])
def dinapoli_detrended_oscillator(close, length=7):
    """Joe DiNapoli's Detrended Oscillator: close - SMA(close, 7) (no
    displacement). HPotter's DiNapoli and "Detrended Price Oscillator"
    strategies compute this (length 14); Hartle's DPO subtracts the SMA
    from ``length/2 + 1`` bars ago (``tv_indicators.dpo``)."""
    return close - k.sma_nb(close, int(length))


@indicator("COMPARATIVE_RS", ["close", "other"], ["crs"])
def comparative_relative_strength(close, other, length=10):
    """Comparative relative strength: SMA(close / other, length)."""
    return k.sma_nb(safe_div(close, other), int(length))


@indicator("GANN_SWING_OSC", ["high", "low"], ["gso"])
def gann_swing_oscillator(high, low, length=5):
    """Gann Swing Oscillator (Robert Krausz, "A W.D. Gann Treasure
    Discovered"): +1 when HHV(high, 5) dipped and rose again
    (HH[2] > HH[1] < HH), -1 when LLV(low, 5) rose and fell again, else the
    previous value (0 at the start). HPotter's combo version is faithful;
    his "Gann Trend Oscillator" runs it on closes with the signs swapped:
    ``-gann_swing_oscillator(close, close)``."""
    n = int(length)
    hh, ll = k.highest_nb(high, n), k.lowest_nb(low, n)
    up = _gt(shift_2d(hh, 2), shift_2d(hh, 1)) & _gt(hh, shift_2d(hh, 1))
    dn = _lt(shift_2d(ll, 2), shift_2d(ll, 1)) & _lt(ll, shift_2d(ll, 1))
    sig = np.where(up, 1.0, np.where(dn, -1.0, NAN))
    out = k.fixnan_nb(sig)
    return np.where(np.isnan(out), 0.0, out)


@indicator("HL_RANGE_HIST", ["high", "low", "close"], ["value", "average"])
def hl_range_histogram(high, low, close, length=13, percent=False):
    """(H-L)/C histogram: high - low (or 100 * (high - low) / close when
    ``percent``) and its SMA (HPotter compares the SMA ``barsback`` bars ago
    with the current value)."""
    v = 100 * (high - low) / close if percent else high - low
    return v, k.sma_nb(np.abs(v), int(length))


@indicator("TREND_ANALYSIS_INDEX", ["close"], ["tai"])
def trend_analysis_index(close, avg_length=28, tai_length=5):
    """Trend Analysis Index: 100 * (HHV - LLV of SMA(close, 28) over 5 bars)
    / close (MetaStock TAI formula), as in HPotter's port."""
    s = k.sma_nb(close, int(avg_length))
    n = int(tai_length)
    return safe_div((k.highest_nb(s, n) - k.lowest_nb(s, n)) * 100, close)


@indicator("WAMI", ["close"], ["wami"])
def wami(close, wma_length=4, ema_length=13):
    """WAMI: EMA(EMA(WMA(mom(close, 1), 4), 13), 13), as in HPotter's port."""
    return k.ema_nb(k.ema_nb(k.wma_nb(change_2d(close), int(wma_length)), int(ema_length)), int(ema_length))


@indicator("VHF_HL", ["high", "low", "close"], ["vhf"])
def vertical_horizontal_filter(high, low, close, length=28, hpotter=False):
    """Adam White's Vertical Horizontal Filter: (HHV(close) - LLV(close)) /
    sum(|change(close)|) - the same as ``tv_indicators.vhf``.
    ``hpotter=True`` takes the range from highs and lows, as HPotter does."""
    n = int(length)
    if hpotter:
        rng = k.highest_nb(high, n) - k.lowest_nb(low, n)
    else:
        rng = k.highest_nb(close, n) - k.lowest_nb(close, n)
    return safe_div(rng, k.sum_nb(np.abs(change_2d(close)), n))


@indicator("ADXR_LAG", ["high", "low", "close"], ["adxr", "adx"])
def adxr(high, low, close, length=14, hpotter=False):
    """Wilder's ADXR = (ADX + ADX[length - 1]) / 2 on TradingView's ADX
    (same as ``tv_indicators.adxr`` / TA-Lib). ``hpotter=True`` averages with
    ADX[length], as HPotter's ADXR and Commodity Selection Index do."""
    n = int(length)
    a = _dmi.core(high, low, close, n, n)[2]
    return (a + shift_2d(a, n if hpotter else n - 1)) / 2, a


@indicator("CSI_WILDER", ["high", "low", "close"], ["csi"])
def commodity_selection_index(high, low, close, length=14, point_value=50.0, margin=3000.0, commission=10.0,
                              hpotter=False):
    """Wilder's Commodity Selection Index ("New Concepts", 1978):
    CSI = ADXR * ATR(14) * [V / sqrt(M) * 1 / (150 + C)] * 100.
    ``hpotter=True`` uses HPotter's ADXR lag (``length`` instead of
    ``length - 1``)."""
    kk = 100 * (point_value / math.sqrt(margin) / (150 + commission))
    a = adxr.core(high, low, close, length, hpotter)[0]
    return kk * atr_2d(high, low, close, int(length)) * a


@njit(cache=True)
def _trend_trader_nb(close, hi_lim, lo_lim):
    out = np.full(close.shape, NAN)
    for c in range(close.shape[1]):
        prev = NAN
        for i in range(close.shape[0]):
            cl, h, l = close[i, c], hi_lim[i, c], lo_lim[i, c]
            if cl > h and cl > l:
                v = h
            elif cl < l and cl < h:
                v = l
            else:
                v = 0.0 if np.isnan(prev) else prev
            out[i, c] = v
            prev = v
    return out


@indicator("TREND_TRADER", ["high", "low", "close"], ["trend_line"])
def trend_trader(high, low, close, length=21, multiplier=3.0):
    """Andrew Abraham's Trend Trader (TASC Sep 1998, "Trading the Trend"):
    avgTR = WMA(TR, 21); the line jumps to HHV[1] - 3 avgTR[1] when close
    is above both that and LLV[1] + 3 avgTR[1], to the lower limit when
    below both, and otherwise holds. HPotter's port is faithful."""
    n = int(length)
    avg = k.wma_nb(atr_2d(high, low, close, 1), n)
    hl = shift_2d(k.highest_nb(high, n), 1) - shift_2d(avg, 1) * multiplier
    ll = shift_2d(k.lowest_nb(low, n), 1) + shift_2d(avg, 1) * multiplier
    return _trend_trader_nb(close, hl, ll)


@njit(cache=True)
def _sofar_nb(x):
    lo = np.full(x.shape, NAN)
    hi = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        mn = 9999999.0
        mx = 0.0
        for i in range(x.shape[0]):
            v = x[i, c]
            if v < mn:
                mn = v
            if v > mx:
                mx = v
            lo[i, c] = mn
            hi[i, c] = mx
    return lo, hi


@indicator("DYNAMO", ["high", "low", "close"], ["dynamo", "osc"])
def dynamo(high, low, close, osc_length=10, ma_length=20):
    """E. Marshall Wall's Dynamic Momentum Oscillator (Futures, Jul 1996) as
    ported by HPotter: osc = SMA(stoch(10), 10); dynamo = midpoint of the
    lowest and highest osc so far - (SMA(osc, 20) - osc)."""
    n = int(osc_length)
    osc = k.sma_nb(stoch_2d(close, high, low, n), n)
    lo, hi = _sofar_nb(osc)
    return (lo + hi) / 2 - (k.sma_nb(osc, int(ma_length)) - osc), osc


@njit(cache=True)
def _ttm_nb(high, low, close):
    level = np.full(close.shape, NAN)
    state = np.full(close.shape, NAN)
    for c in range(close.shape[1]):
        sw = NAN
        sbs = NAN
        cs = NAN
        for i in range(close.shape[0]):
            ts = False
            tb = False
            if i >= 3:
                c0, c1, c2, c3 = close[i, c], close[i - 1, c], close[i - 2, c], close[i - 3, c]
                ts = c1 < c0 and (c2 < c1 or c3 < c1)
                tb = c1 > c0 and (c2 > c1 or c3 > c1)
            prev_sw = sw
            nsw = 1.0 if ts else (0.0 if tb else (0.0 if np.isnan(sw) else sw))
            if ts and prev_sw == 0:
                nsbs, ncs = high[i, c], 1.0
            elif tb and prev_sw == 1:
                nsbs, ncs = low[i, c], 0.0
            else:
                nsbs = 0.0 if np.isnan(sbs) else sbs
                ncs = 0.0 if np.isnan(cs) else cs
            sw, sbs, cs = nsw, nsbs, ncs
            level[i, c] = sbs
            state[i, c] = cs
    return level, state


@indicator("TTM_SCALPER", ["high", "low", "close"], ["level", "state"])
def ttm_scalper(high, low, close):
    """TTM Scalper (John Carter, "Mastering the Trade") as approximated in
    HPotter's port: a sell trigger is a higher close after a bar that
    closed above one of the two before it; ``level`` is the high of the
    first sell trigger after a buy phase (state 1) or the low of the first
    buy trigger after a sell phase (state 0)."""
    return _ttm_nb(high, low, close)


@njit(cache=True)
def _three_line_nb(close):
    out = np.full(close.shape, NAN)
    up = np.full(close.shape, NAN)
    dn = np.full(close.shape, NAN)
    for c in range(close.shape[1]):
        tr1 = NAN
        u1 = u11 = u21 = u31 = NAN
        for i in range(close.shape[0]):
            cl = close[i, c]
            tr = 1.0
            u = u1_ = u2_ = u3_ = cl
            if tr1 == 1:
                if cl > u1:
                    u3_, u2_, u1_, u, tr = u21, u11, u1, cl, 1.0
                elif cl < u31:
                    u3_, u2_, u1_, u, tr = u11, u11, u11, cl, -1.0
                else:
                    tr = 1.0
            else:
                if cl > u31:
                    u3_, u2_, u1_, u, tr = u11, u11, u11, cl, 1.0
                elif cl < u1:
                    u3_, u2_, u1_, u, tr = u21, u11, u1, cl, -1.0
                else:
                    tr = -1.0
            out[i, c] = tr
            up[i, c] = u
            dn[i, c] = u3_
            tr1, u1, u11, u21, u31 = tr, u, u1_, u2_, u3_
    return out, up, dn


@indicator("HPOTTER_THREE_LINE_BREAK", ["close"], ["trend", "line", "line3"])
def hpotter_three_line_break(close):
    """HPotter's "modified" Three Line Break: a close-only state machine on
    the last line and the line three back (``trend`` +1/-1). It is his own
    variant, not Nison's three-line-break chart (which needs a non-time
    axis); a literal port."""
    return _three_line_nb(close)


@njit(cache=True)
def _kwan_nb(val, mom, n):
    out = np.full(val.shape, NAN)
    for c in range(val.shape[1]):
        buf = np.full(val.shape[0] + 1, NAN)
        size = 1                       # array.new_float(1, na)
        for i in range(val.shape[0]):
            m = mom[i, c]
            if not np.isnan(m) and m != 0:
                buf[size] = val[i, c]
                size += 1
            s = 0.0
            if size > n:
                for j in range(size - n, size):
                    s += buf[j]
            out[i, c] = s / n
    return out


@indicator("KWAN_NRP", ["open", "high", "low", "close"], ["knrp"])
def kwan_nrp(open, high, low, close, momentum_length=9, rsi_length=9, stoch_length=9, nrp_length=2):
    """Kwan NRP as ported by HPotter: the ``nrp_length``-bar average of
    stoch(open, high, low, 9) * RSI(open, 9) / (100 * close / close[9]),
    keeping only bars where the momentum ratio exists (0 until enough
    values have been collected, na while they include na)."""
    mom = safe_div(close, shift_2d(close, int(momentum_length))) * 100
    val = stoch_2d(open, high, low, int(stoch_length)) * rsi_2d(open, int(rsi_length)) / mom
    return _kwan_nb(val, mom, int(nrp_length))


@njit(cache=True)
def _smi_hays_nb(open_, close, sess, first_bars, last_bars, start):
    out = np.full(close.shape, NAN)
    for c in range(close.shape[1]):
        smi_done = start
        cur = start
        prev_close = NAN
        s0 = 0
        for i in range(close.shape[0]):
            if i == 0 or sess[i, c] != sess[i - 1, c]:
                if i > 0:
                    smi_done = cur
                    prev_close = close[i - 1, c]
                s0 = i
            f_end = s0 + first_bars - 1
            if i < f_end:
                cur = smi_done
            else:
                ref = open_[s0, c] if np.isnan(prev_close) else prev_close
                open_move = close[f_end, c] - ref
                j = i - last_bars
                if j < f_end:
                    j = f_end
                cur = smi_done - open_move + (close[i, c] - close[j, c])
            out[i, c] = cur
    return out


@indicator("SMART_MONEY_INDEX", ["open", "close", "session"], ["smi"])
def smart_money_index(open, close, session, first_bars=1, last_bars=1, start=0.0):
    """Don Hays' Smart Money Index on intraday bars:
    SMI = previous session's SMI - opening move + last-period move, where the
    opening move is the change from the previous session's close to the
    close of the first ``first_bars`` bars (e.g. 30 minutes) and the last
    move is the change over the last ``last_bars`` bars (e.g. 1 hour).

    ``session`` = one id per day (``tv_indicators.session_ids``). Inside a
    session the value is provisional (the last-period move so far); it is
    Hays' figure on the session's last bar. No look-ahead.
    """
    return _smi_hays_nb(open, close, np.nan_to_num(session, nan=-1.0), int(first_bars), int(last_bars),
                        float(start))


@indicator("SMART_MONEY_INDEX_HP", ["open", "close", "htf_open", "htf_close"], ["smi"])
def smart_money_index_hpotter(open, close, htf_open, htf_close):
    """HPotter's Smart Money Index, for reproducing his strategies:
    smi = nz(smi[1], 1) - (open - close) + (htf_open - htf_close), where
    ``htf_open`` / ``htf_close`` are ``request.security(tf, open[1] /
    close[1])`` - the previous higher-timeframe bar, aligned to the chart.
    It adds every bar's own change and subtracts the previous HTF bar's
    change, which is not Hays' first-half-hour / last-hour rule
    (:func:`smart_money_index`)."""
    return _nzcum_nb(-(open - close) + (htf_open - htf_close), 1.0)


@indicator("KASE_DEV_STOPS", ["high", "low", "close"], ["warning", "dev1", "dev2", "dev3", "direction"])
def kase_dev_stops(high, low, close, length=30, dev_length=30, mult1=1.0, mult2=2.2, mult3=3.6, hpotter=False):
    """Cynthia Kase's Dev-Stops ("Trading with the Odds"; "Kase Dev Stop",
    2005): the mean and standard deviation of the two-bar true range over
    ``dev_length`` bars, placed at 0 (warning), 1, 2.2 and 3.6 deviations.
    Long stops (``direction`` > 0) are HHV(high - avg - m * sd, dev_length),
    short stops LLV(low + avg + m * sd); ``direction`` is HPotter's
    WMA(RWH - RWL, 3) of Kase's random-walk index over ``length``.

    ``hpotter=True``: HPotter's version - the two-bar high-low range
    (no prior close), 20 bars, and 1/2/3 deviations (his Val1..Val4 are
    warning, dev1, dev2, dev3 here).
    """
    n = int(length)
    a = atr_2d(high, low, close, n) * math.sqrt(n)
    rwh = safe_div(high - shift_2d(low, n), a)
    rwl = safe_div(shift_2d(high, n) - low, a)
    pk = k.wma_nb(rwh - rwl, 3)
    if hpotter:
        m = 20
        mults = (1.0, 2.0, 3.0)
        dtr = k.highest_nb(high, 2) - k.lowest_nb(low, 2)
    else:
        m = int(dev_length)
        mults = (float(mult1), float(mult2), float(mult3))
        c2 = shift_2d(close, 2)
        dtr = np.fmax(k.highest_nb(high, 2), c2) - np.fmin(k.lowest_nb(low, 2), c2)
        dtr[np.isnan(c2)] = NAN
    avg = k.sma_nb(dtr, m)
    sd = k.stdev_nb(dtr, m)
    outs = []
    for mu in (0.0,) + mults:
        outs.append(np.where(_gt(pk, 0), k.highest_nb(high - avg - mu * sd, m), k.lowest_nb(low + avg + mu * sd, m)))
    return tuple(outs) + (pk,)


# Keep these out of tv_indicators' registry so the main library is unchanged.
EXTRA_HPOTTER = {name: REGISTRY.pop(name) for name in list(REGISTRY)
                 if name not in _BEFORE or REGISTRY[name] is not _BEFORE[name]}

__all__ = sorted(fn.__name__ for fn in EXTRA_HPOTTER.values())
