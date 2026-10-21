"""ABCD pivot patterns with Fibonacci ratio tests and a structure bracket, 1-minute bars: a confirmed low-high-low-high sequence of 5 / 5 pivots whose retracement ratios fall in 0.5-0.7 and 1.1-1.35, with the close
between the last pivot low and the older pivot high, buys once per pattern; the mirror sells; stop beyond the last pivot by one true range, target 1.5x the risk capped at the older pivot; reversing.
Port of FMZ strategy #437740 "Pivot Point and Fibonacci Retracement Based Automatic Trend Following Strategy" (ABCDS).

FMZ source id: 437740

Source
    https://www.fmz.com/strategy/437740 (PineScript v5, FMZ last modified 2024-01-05 11:34:17).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 99-201), pivot length 5
    pivots ph / pl = pivothigh / pivotlow(5, 5) (confirmed 5 bars later);  formlong = oldphb < oldplb < currphb < currplb, ratio1 = (currph - oldpl) / (oldph - oldpl) in (0.5, 0.7), ratio2 = (currph - currpl) / (currph - oldpl) in (1.1, 1.35)
    longCond and close < oldph and close > currpl and a new pattern -> entry Long, exit(limit = min(close + 1.5 (close - sl), oldph), stop = sl = currpl - tr);  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pivots are confirmed five bars after the pivot bar (no future read). The pivot bookkeeping follows the
      script (a bar with a pivot high updates only the highs; else a pivot low updates the lows). The
      bracket levels are the signal bar's, as distances from its close (sl_stop / tp_stop), shifted one bar
      inside stops() and re-based on the fill; a level on the wrong side of the close gives no order.
      signalid keeps one entry per pattern. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      The commission is sizing. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, pivot ratios and structure levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commission stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437740_abcd_pivot_fib_bracket"
FAMILY = "reversal_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [5, 10],
}
DEFAULT_PARAMS = {"length": 5, "rr": 1.5}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _pivots(h, lo, n):
    """pivothigh / pivotlow(n, n): at bar t the value of bar t - n when it is a strict extreme over the
    n bars before and the n bars after it (as #434470), else nan."""
    m = len(h)
    ph, pl = np.full(m, np.nan), np.full(m, np.nan)
    for t in range(2 * n, m):
        c = t - n
        if h[c] > h[c - n:c].max() and h[c] > h[c + 1:t + 1].max():
            ph[t] = h[c]
        if lo[c] < lo[c - n:c].min() and lo[c] < lo[c + 1:t + 1].min():
            pl[t] = lo[c]
    return ph, pl


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    pc = c.shift(1)
    trv = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).to_numpy()
    ph, pl = _pivots(hv, lv, n)
    m = len(cv)
    lc, sc = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl, tp = np.full(m, np.nan), np.full(m, np.nan)
    cph = cphb = oph = ophb = 0.0
    cpl = cplb = opl = oplb = 0.0
    sid = 0.0
    rr = float(p["rr"])
    with np.errstate(divide="ignore", invalid="ignore"):
        for t in range(m):
            if not np.isnan(ph[t]):
                oph, ophb, cph, cphb = cph, cphb, ph[t], float(t - n)
            elif not np.isnan(pl[t]):
                opl, oplb, cpl, cplb = cpl, cplb, pl[t], float(t - n)
            fl = ophb < oplb and oplb < cphb and cphb < cplb
            r1 = (cph - opl) / (oph - opl)
            r2 = (cph - cpl) / (cph - opl)
            if fl and 0.5 < r1 < 0.7 and 1.1 < r2 < 1.35 and cv[t] < oph and cv[t] > cpl and sid != oplb:
                sid = oplb
                stop = cpl - trv[t]
                tgt = min((cv[t] - stop) * rr + cv[t], oph)
                lc[t] = True
                sl[t], tp[t] = (cv[t] - stop) / cv[t], (tgt - cv[t]) / cv[t]
                continue
            fs = oplb < ophb and ophb < cplb and cplb < cphb
            s1 = (oph - cpl) / (oph - opl)
            s2 = (cph - cpl) / (oph - cpl)
            if fs and 0.5 < s1 < 0.7 and 1.1 < s2 < 1.35 and cv[t] > opl and cv[t] < cph and sid != ophb:
                sid = ophb
                stop = cph + trv[t]
                tgt = max(cv[t] - (stop - cv[t]) * rr, opl)
                sc[t] = True
                sl[t], tp[t] = (stop - cv[t]) / cv[t], (cv[t] - tgt) / cv[t]
    ix = bars_df.index
    sl_s = pd.Series(sl, index=ix)
    tp_s = pd.Series(tp, index=ix)
    return pd.Series(lc, index=ix), pd.Series(sc, index=ix), sl_s.where(sl_s > 0), tp_s.where(tp_s > 0)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lc, sc, _, _ = _setup(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return lc, false, sc, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _setup(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
