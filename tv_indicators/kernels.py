"""Numba kernels that reproduce Pine Script ``ta.*`` built-ins.

Every kernel takes 2D float64 arrays shaped ``(n_bars, n_columns)`` and works
column by column, so one call handles many symbols or parameter sets at once.
That is also the shape vectorbt hands to an ``apply_func``.

Pine semantics that are mirrored on purpose:

* A window that contains ``na`` gives ``na`` (``ta.sma``, ``ta.stdev``, ...).
* ``ta.ema`` and ``ta.rma`` seed with the SMA of the first ``length`` valid
  values and only then switch to the recursive formula. If the source becomes
  ``na`` later on, the state resets and seeds again (Pine's
  ``na(sum[1]) ? ta.sma(src, length) : ...``).
* Comparisons with ``na`` are false, ``nz(x)`` turns ``na`` into 0.
"""

import numpy as np
from numba import njit

NAN = np.nan


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

@njit(cache=True)
def _nz(x, repl=0.0):
    return repl if np.isnan(x) else x


@njit(cache=True)
def _max2(a, b):
    # Pine's math.max returns na when either argument is na.
    if np.isnan(a) or np.isnan(b):
        return NAN
    return a if a > b else b


@njit(cache=True)
def _min2(a, b):
    if np.isnan(a) or np.isnan(b):
        return NAN
    return a if a < b else b


@njit(cache=True)
def _window_ok(x, i, c, n):
    if i < n - 1:
        return False
    for k in range(n):
        if np.isnan(x[i - k, c]):
            return False
    return True


# ---------------------------------------------------------------------------
# Rolling windows
# ---------------------------------------------------------------------------

@njit(cache=True)
def sum_nb(x, n):
    """``math.sum(x, n)``."""
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        s = 0.0
        n_nan = 0
        for i in range(x.shape[0]):
            v = x[i, c]
            if np.isnan(v):
                n_nan += 1
            else:
                s += v
            if i >= n:
                old = x[i - n, c]
                if np.isnan(old):
                    n_nan -= 1
                else:
                    s -= old
            if i >= n - 1 and n_nan == 0:
                out[i, c] = s
    return out


@njit(cache=True)
def sma_nb(x, n):
    """``ta.sma(x, n)``."""
    return sum_nb(x, n) / n


@njit(cache=True)
def wma_nb(x, n):
    """``ta.wma(x, n)``: linear weights, newest bar weighted ``n``."""
    out = np.full(x.shape, NAN)
    norm = n * (n + 1) / 2.0
    for c in range(x.shape[1]):
        for i in range(n - 1, x.shape[0]):
            s = 0.0
            for k in range(n):
                s += x[i - k, c] * (n - k)
            out[i, c] = s / norm  # na propagates through the sum
    return out


@njit(cache=True)
def stdev_nb(x, n):
    """``ta.stdev(x, n)`` with Pine's default ``biased=true`` (population)."""
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for i in range(n - 1, x.shape[0]):
            m = 0.0
            for k in range(n):
                m += x[i - k, c]
            m /= n
            ss = 0.0
            for k in range(n):
                d = x[i - k, c] - m
                ss += d * d
            out[i, c] = np.sqrt(ss / n)
    return out


@njit(cache=True)
def dev_nb(x, n):
    """``ta.dev(x, n)``: mean absolute deviation from the SMA."""
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for i in range(n - 1, x.shape[0]):
            m = 0.0
            for k in range(n):
                m += x[i - k, c]
            m /= n
            s = 0.0
            for k in range(n):
                s += abs(x[i - k, c] - m)
            out[i, c] = s / n
    return out


@njit(cache=True)
def highest_nb(x, n):
    """``ta.highest(x, n)``."""
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for i in range(n - 1, x.shape[0]):
            if not _window_ok(x, i, c, n):
                continue
            h = x[i, c]
            for k in range(1, n):
                if x[i - k, c] > h:
                    h = x[i - k, c]
            out[i, c] = h
    return out


@njit(cache=True)
def lowest_nb(x, n):
    """``ta.lowest(x, n)``."""
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for i in range(n - 1, x.shape[0]):
            if not _window_ok(x, i, c, n):
                continue
            lo = x[i, c]
            for k in range(1, n):
                if x[i - k, c] < lo:
                    lo = x[i - k, c]
            out[i, c] = lo
    return out


@njit(cache=True)
def highestbars_nb(x, n):
    """``ta.highestbars(x, n)``: offset (<= 0) to the highest bar.

    Ties resolve to the most recent bar, as TA-Lib does.
    """
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for i in range(n - 1, x.shape[0]):
            if not _window_ok(x, i, c, n):
                continue
            best = 0
            for k in range(1, n):
                if x[i - k, c] > x[i - best, c]:
                    best = k
            out[i, c] = -best
    return out


@njit(cache=True)
def lowestbars_nb(x, n):
    """``ta.lowestbars(x, n)``: offset (<= 0) to the lowest bar."""
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for i in range(n - 1, x.shape[0]):
            if not _window_ok(x, i, c, n):
                continue
            best = 0
            for k in range(1, n):
                if x[i - k, c] < x[i - best, c]:
                    best = k
            out[i, c] = -best
    return out


@njit(cache=True)
def linreg_nb(x, n, offset):
    """``ta.linreg(x, n, offset)``: least-squares line value at ``n-1-offset``.

    The oldest bar of the window is x=0 and the current bar is x=n-1.
    """
    out = np.full(x.shape, NAN)
    if n == 1:
        return x.copy()
    sx = n * (n - 1) / 2.0
    sxx = (n - 1) * n * (2 * n - 1) / 6.0
    denom = n * sxx - sx * sx
    for c in range(x.shape[1]):
        for i in range(n - 1, x.shape[0]):
            sy = 0.0
            sxy = 0.0
            for j in range(n):
                y = x[i - (n - 1) + j, c]
                sy += y
                sxy += j * y
            slope = (n * sxy - sx * sy) / denom
            intercept = (sy - slope * sx) / n
            out[i, c] = intercept + slope * (n - 1 - offset)
    return out


@njit(cache=True)
def percentrank_nb(x, n):
    """``ta.percentrank(x, n)``: % of the previous ``n`` values <= current."""
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        for i in range(n, x.shape[0]):
            v = x[i, c]
            if np.isnan(v):
                continue
            cnt = 0
            ok = True
            for k in range(1, n + 1):
                p = x[i - k, c]
                if np.isnan(p):
                    ok = False
                    break
                if p <= v:
                    cnt += 1
            if ok:
                out[i, c] = 100.0 * cnt / n
    return out


@njit(cache=True)
def alma_nb(x, n, offset, sigma, floor):
    """``ta.alma(x, n, offset, sigma, floor)``."""
    out = np.full(x.shape, NAN)
    m = offset * (n - 1)
    if floor:
        m = np.floor(m)
    s = n / sigma
    w = np.empty(n)
    for j in range(n):
        w[j] = np.exp(-((j - m) ** 2) / (2.0 * s * s))
    norm = w.sum()
    for c in range(x.shape[1]):
        for i in range(n - 1, x.shape[0]):
            acc = 0.0
            for j in range(n):
                acc += x[i - (n - 1) + j, c] * w[j]  # j=0 is the oldest bar
            out[i, c] = acc / norm
    return out


# ---------------------------------------------------------------------------
# Recursive averages
# ---------------------------------------------------------------------------

@njit(cache=True)
def ewm_nb(x, n, alpha):
    """SMA-seeded exponential smoothing shared by ``ta.ema`` and ``ta.rma``."""
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        state = NAN
        run = 0
        for i in range(x.shape[0]):
            v = x[i, c]
            if np.isnan(v):
                run = 0
                state = NAN
            else:
                run += 1
                if np.isnan(state):
                    if run >= n:
                        s = 0.0
                        for k in range(n):
                            s += x[i - k, c]
                        state = s / n
                else:
                    state = alpha * v + (1.0 - alpha) * state
            out[i, c] = state
    return out


@njit(cache=True)
def ema_nb(x, n):
    """``ta.ema(x, n)``, alpha = 2 / (n + 1)."""
    return ewm_nb(x, n, 2.0 / (n + 1.0))


@njit(cache=True)
def rma_nb(x, n):
    """``ta.rma(x, n)`` (Wilder / SMMA), alpha = 1 / n."""
    return ewm_nb(x, n, 1.0 / n)


@njit(cache=True)
def mcginley_nb(src, ema_seed, n):
    """McGinley Dynamic as in TradingView's built-in script."""
    out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        prev = NAN
        for i in range(src.shape[0]):
            if np.isnan(prev):
                cur = ema_seed[i, c]
            else:
                cur = prev + (src[i, c] - prev) / (n * (src[i, c] / prev) ** 4)
            out[i, c] = cur
            prev = cur
    return out


@njit(cache=True)
def kama_nb(x, n, fast, slow):
    """Kaufman Adaptive MA, seeded like TA-Lib (previous close)."""
    out = np.full(x.shape, NAN)
    fsc = 2.0 / (fast + 1.0)
    ssc = 2.0 / (slow + 1.0)
    for c in range(x.shape[1]):
        prev = NAN
        for i in range(n, x.shape[0]):
            vol = 0.0
            for k in range(n):
                vol += abs(x[i - k, c] - x[i - k - 1, c])
            change = abs(x[i, c] - x[i - n, c])
            er = 0.0 if vol == 0 else change / vol
            sc = (er * (fsc - ssc) + ssc) ** 2
            if np.isnan(prev):
                prev = x[i - 1, c]
            prev = prev + sc * (x[i, c] - prev)
            out[i, c] = prev
    return out


@njit(cache=True)
def cum_nb(x):
    """``ta.cum(x)``; ``na`` contributes 0, output is ``na`` until the first value."""
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        s = 0.0
        seen = False
        for i in range(x.shape[0]):
            v = x[i, c]
            if not np.isnan(v):
                s += v
                seen = True
            if seen:
                out[i, c] = s
    return out


@njit(cache=True)
def fixnan_nb(x):
    """``fixnan(x)``: carry the last non-na value forward."""
    out = x.copy()
    for c in range(x.shape[1]):
        last = NAN
        for i in range(x.shape[0]):
            if np.isnan(x[i, c]):
                out[i, c] = last
            else:
                last = x[i, c]
    return out


@njit(cache=True)
def tr_nb(high, low, close, handle_na):
    """``ta.tr(handle_na)``. With ``handle_na`` the first bar is ``high - low``."""
    out = np.full(high.shape, NAN)
    for c in range(high.shape[1]):
        for i in range(high.shape[0]):
            hl = high[i, c] - low[i, c]
            pc = close[i - 1, c] if i > 0 else NAN
            if np.isnan(pc):
                if handle_na:
                    out[i, c] = hl
            else:
                out[i, c] = max(hl, abs(high[i, c] - pc), abs(low[i, c] - pc))
    return out


# ---------------------------------------------------------------------------
# Stateful indicators
# ---------------------------------------------------------------------------

@njit(cache=True)
def supertrend_nb(src, close, atr, factor):
    """``ta.supertrend``. Direction is TradingView's: -1 = up trend, 1 = down."""
    st_out = np.full(src.shape, NAN)
    dir_out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        prev_lb = NAN
        prev_ub = NAN
        prev_st = NAN
        for i in range(src.shape[0]):
            ub = src[i, c] + factor * atr[i, c]
            lb = src[i, c] - factor * atr[i, c]
            plb = _nz(prev_lb)
            pub = _nz(prev_ub)
            pc = close[i - 1, c] if i > 0 else NAN
            if not (lb > plb or pc < plb):
                lb = plb
            if not (ub < pub or pc > pub):
                ub = pub
            if i == 0 or np.isnan(atr[i - 1, c]):
                d = 1.0
            elif prev_st == pub:
                d = -1.0 if close[i, c] > ub else 1.0
            else:
                d = 1.0 if close[i, c] < lb else -1.0
            st = lb if d == -1.0 else ub
            if not np.isnan(atr[i, c]):
                st_out[i, c] = st
                dir_out[i, c] = d
            prev_lb = lb
            prev_ub = ub
            prev_st = st
    return st_out, dir_out


@njit(cache=True)
def sar_nb(high, low, close, start, inc, maximum):
    """``ta.sar(start, inc, max)``, a direct port of Pine's reference code."""
    out = np.full(high.shape, NAN)
    for c in range(high.shape[1]):
        result = NAN
        max_min = NAN
        accel = NAN
        is_below = False
        for i in range(high.shape[0]):
            first_trend_bar = False
            if i == 1:
                if close[i, c] > close[i - 1, c]:
                    is_below = True
                    max_min = high[i, c]
                    result = low[i - 1, c]
                else:
                    is_below = False
                    max_min = low[i, c]
                    result = high[i - 1, c]
                first_trend_bar = True
                accel = start
            if i == 0:
                continue
            result = result + accel * (max_min - result)
            if is_below:
                if result > low[i, c]:
                    first_trend_bar = True
                    is_below = False
                    result = max(high[i, c], max_min)
                    max_min = low[i, c]
                    accel = start
            else:
                if result < high[i, c]:
                    first_trend_bar = True
                    is_below = True
                    result = min(low[i, c], max_min)
                    max_min = high[i, c]
                    accel = start
            if not first_trend_bar:
                if is_below:
                    if high[i, c] > max_min:
                        max_min = high[i, c]
                        accel = min(accel + inc, maximum)
                else:
                    if low[i, c] < max_min:
                        max_min = low[i, c]
                        accel = min(accel + inc, maximum)
            if is_below:
                result = min(result, low[i - 1, c])
                if i > 1:
                    result = min(result, low[i - 2, c])
            else:
                result = max(result, high[i - 1, c])
                if i > 1:
                    result = max(result, high[i - 2, c])
            out[i, c] = result
    return out


@njit(cache=True)
def fisher_nb(src, hi, lo):
    """Fisher Transform (TradingView built-in). Returns (fisher, trigger)."""
    fish_out = np.full(src.shape, NAN)
    trig_out = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        prev_val = NAN
        prev_fish = NAN
        for i in range(src.shape[0]):
            rng = hi[i, c] - lo[i, c]
            if np.isnan(rng) or rng == 0:
                val = NAN
            else:
                val = 0.66 * ((src[i, c] - lo[i, c]) / rng - 0.5) + 0.67 * _nz(prev_val)
                if val > 0.99:
                    val = 0.999
                elif val < -0.99:
                    val = -0.999
            if np.isnan(val):
                fish = NAN
            else:
                fish = 0.5 * np.log((1 + val) / (1 - val)) + 0.5 * _nz(prev_fish)
            fish_out[i, c] = fish
            trig_out[i, c] = prev_fish
            prev_val = val
            prev_fish = fish
    return fish_out, trig_out


@njit(cache=True)
def chandelier_nb(long_base, short_base, atr_mult, close):
    """Chandelier Exit [everget]. Returns (long_stop, short_stop, dir, buy, sell)."""
    shape = close.shape
    ls_out = np.full(shape, NAN)
    ss_out = np.full(shape, NAN)
    dir_out = np.full(shape, NAN)
    buy = np.zeros(shape, dtype=np.bool_)
    sell = np.zeros(shape, dtype=np.bool_)
    for c in range(shape[1]):
        prev_ls = NAN
        prev_ss = NAN
        d = 1.0
        prev_d = NAN
        for i in range(shape[0]):
            ls = long_base[i, c] - atr_mult[i, c]
            ss = short_base[i, c] + atr_mult[i, c]
            ls_prev = ls if np.isnan(prev_ls) else prev_ls
            ss_prev = ss if np.isnan(prev_ss) else prev_ss
            pc = close[i - 1, c] if i > 0 else NAN
            if pc > ls_prev:
                ls = _max2(ls, ls_prev)
            if pc < ss_prev:
                ss = _min2(ss, ss_prev)
            if close[i, c] > ss_prev:
                d = 1.0
            elif close[i, c] < ls_prev:
                d = -1.0
            ls_out[i, c] = ls
            ss_out[i, c] = ss
            dir_out[i, c] = d
            buy[i, c] = d == 1.0 and prev_d == -1.0
            sell[i, c] = d == -1.0 and prev_d == 1.0
            prev_ls = ls
            prev_ss = ss
            prev_d = d
    return ls_out, ss_out, dir_out, buy, sell


@njit(cache=True)
def utbot_nb(src, nloss):
    """UT Bot Alerts [QuantNomad]. Returns (trailing_stop, pos)."""
    stop_out = np.full(src.shape, NAN)
    pos_out = np.zeros(src.shape)
    for c in range(src.shape[1]):
        prev_stop = NAN
        prev_pos = 0.0
        for i in range(src.shape[0]):
            p = _nz(prev_stop)
            s = src[i, c]
            s1 = src[i - 1, c] if i > 0 else NAN
            nl = nloss[i, c]
            if s > p and s1 > p:
                stop = _max2(p, s - nl)
            elif s < p and s1 < p:
                stop = _min2(p, s + nl)
            elif s > p:
                stop = s - nl
            else:
                stop = s + nl
            if s1 < p and s > p:
                pos = 1.0
            elif s1 > p and s < p:
                pos = -1.0
            else:
                pos = prev_pos
            stop_out[i, c] = stop
            pos_out[i, c] = pos
            prev_stop = stop
            prev_pos = pos
    return stop_out, pos_out


@njit(cache=True)
def updown_nb(x):
    """Streak length used by Connors RSI (positive = up streak)."""
    out = np.full(x.shape, NAN)
    for c in range(x.shape[1]):
        prev = NAN
        for i in range(x.shape[0]):
            p1 = x[i - 1, c] if i > 0 else NAN
            if x[i, c] == p1:
                ud = 0.0
            elif x[i, c] > p1:
                ud = 1.0 if _nz(prev) <= 0 else _nz(prev) + 1
            else:
                ud = -1.0 if _nz(prev) >= 0 else _nz(prev) - 1
            out[i, c] = ud
            prev = ud
    return out


@njit(cache=True)
def heikin_ashi_nb(open_, high, low, close):
    ha_c = (open_ + high + low + close) / 4.0
    ha_o = np.full(open_.shape, NAN)
    for c in range(open_.shape[1]):
        prev_o = NAN
        for i in range(open_.shape[0]):
            if np.isnan(prev_o):
                o = (open_[i, c] + close[i, c]) / 2.0
            else:
                o = (prev_o + ha_c[i - 1, c]) / 2.0
            ha_o[i, c] = o
            prev_o = o
    ha_h = np.maximum(high, np.maximum(ha_o, ha_c))
    ha_l = np.minimum(low, np.minimum(ha_o, ha_c))
    return ha_o, ha_h, ha_l, ha_c


@njit(cache=True)
def vwap_nb(src, volume, session):
    """Anchored ``ta.vwap`` with the volume-weighted standard deviation."""
    vw = np.full(src.shape, NAN)
    sd = np.full(src.shape, NAN)
    for c in range(src.shape[1]):
        sv = 0.0
        svp = 0.0
        svp2 = 0.0
        for i in range(src.shape[0]):
            if i == 0 or session[i, c] != session[i - 1, c]:
                sv = 0.0
                svp = 0.0
                svp2 = 0.0
            v = volume[i, c]
            p = src[i, c]
            if not (np.isnan(v) or np.isnan(p)):
                sv += v
                svp += v * p
                svp2 += v * p * p
            if sv > 0:
                m = svp / sv
                vw[i, c] = m
                var = svp2 / sv - m * m
                sd[i, c] = np.sqrt(var) if var > 0 else 0.0
    return vw, sd
