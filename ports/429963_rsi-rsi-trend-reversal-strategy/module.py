"""RSI(5) divergences, long only, hourly bars: a regular or hidden bullish divergence at a confirmed RSI pivot low goes
long; RSI crossing above 75 or a regular bearish divergence closes the long.
Port of FMZ strategy #429963 "RSI趋势反转策略RSI-Trend-Reversal-Strategy" (RSI Divergence Indicator).

FMZ source id: 429963

Source
    https://www.fmz.com/strategy/429963 (PineScript v4, FMZ last modified 2023-10-23 17:04:13).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 187-355), RSI 5, pivots 5 / 5, range 5-60 bars; bull, hidden bull and bear on
    plFound = pivotlow(rsi, 5, 5) found (the pivot is 5 bars back); phFound likewise for highs
    bull = low[5] < previous pivot's low[5] and rsi[5] > previous pivot's rsi[5] and the previous pivot 5-60 bars ago
    hidden bull = low[5] > previous low[5] and rsi[5] < previous rsi[5] (same range); bull or hidden bull -> entry long
    bear = high[5] > previous pivot high[5] and rsi[5] < previous rsi[5]; crossover(rsi, 75) or bear -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * A pivot low at bar t - 5 is confirmed at bar t (5 bars each side): no look-ahead. Pivot test: the
      value is strictly below the 5 values on each side (stated reading of pivotlow); highs mirror.
    * valuewhen(plFound, x[5], 1) is the value at the previous confirmed pivot; _inRange(plFound[1]) needs
      the bars since the last pivot before this bar to be within 5-60.
    * Long only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; pivots confirmed after 5 bars.
    2 generic: PASS, RSI levels and price comparisons between pivots.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() fixed quantity 2 and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND366941 (4 members, best partner #366941, Jaccard 0.742); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429963_rsi_divergence_long"
FAMILY = "macd_divergence"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [5, 14],
    "lb": [5, 3],
}
DEFAULT_PARAMS = {"rsi_len": 5, "lb": 5, "range_upper": 60, "range_lower": 5, "exit_level": 75}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _pivots(v, lb, low):
    m = len(v)
    found = np.zeros(m, dtype=bool)
    for t in range(2 * lb, m):
        c = v[t - lb]
        if np.isnan(c):
            continue
        win = np.concatenate((v[t - 2 * lb:t - lb], v[t - lb + 1:t + 1]))
        if np.isnan(win).any():
            continue
        found[t] = bool((c < win).all()) if low else bool((c > win).all())
    return found


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    r = _rsi(bars_df["close"], int(p["rsi_len"]))
    rv = r.to_numpy()
    lb = int(p["lb"])
    pl, ph = _pivots(rv, lb, True), _pivots(rv, lb, False)
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    ru, rl = int(p["range_upper"]), int(p["range_lower"])
    last_pl = last_ph = None             # (bar index, rsi[lb], low / high[lb]) of the last confirmed pivot
    for t in range(m):
        bull = hbull = bear = False
        if pl[t] and last_pl is not None:
            bars = t - 1 - last_pl[0]
            ok = rl <= bars <= ru
            o_now, p_now = rv[t - lb], lo[t - lb]
            bull = ok and o_now > last_pl[1] and p_now < last_pl[2]
            hbull = ok and o_now < last_pl[1] and p_now > last_pl[2]
        if ph[t] and last_ph is not None:
            bars = t - 1 - last_ph[0]
            ok = rl <= bars <= ru
            bear = ok and rv[t - lb] < last_ph[1] and h[t - lb] > last_ph[2]
        if pl[t]:
            last_pl = (t, rv[t - lb], lo[t - lb])
        if ph[t]:
            last_ph = (t, rv[t - lb], h[t - lb])
        xo = t >= 1 and rv[t] > p["exit_level"] and rv[t - 1] <= p["exit_level"]
        le[t] = bull or hbull
        lx[t] = (bool(xo) or bear) and not le[t]
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
