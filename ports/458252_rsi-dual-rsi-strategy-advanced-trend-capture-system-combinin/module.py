"""RSI 14 threshold crossings after a divergence has ever been seen, 2-hour bars: once a bullish RSI divergence has appeared, every RSI cross back over 30 goes long; once a bearish one has appeared, every RSI cross under 70 goes short; reversing.
Port of FMZ strategy #458252 "双重RSI策略结合背离与交叉的高级趋势捕捉系统-Dual-RSI-Strategy-Advanced-Trend-Capture-System-Combining-Divergence-and-Crossover" (Combined RSI Strategies).

FMZ source id: 458252

Source
    https://www.fmz.com/strategy/458252 (PineScript v4, FMZ last modified 2024-07-31 11:55:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 169-251), RSI 14; divergence lookback 90 bars (highestbars / lowestbars of the RSI); thresholds 30 / 70
    max / max_rsi = close / rsi on the bar of the 90-bar RSI high, else kept, then raised by a higher close / RSI (min likewise)
    max[1] > max[2] and rsi[1] < max_rsi and rsi <= rsi[1] -> divbear = true;  min[1] < min[2] and rsi[1] > min_rsi and rsi >= rsi[1] -> divbull = true
    divbull and crossover(rsi, 30) -> entry Long;  divbear and crossunder(rsi, 70) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Version 4. divbull and divbear are var flags that are set and never cleared, so after the first
      divergence of each kind the entries are the plain threshold crossings, as written. The bar of the
      90-bar RSI high is a bar whose RSI is at the window's high (ties read as the current bar); the
      window is not counted before 90 RSI values exist. There is no exit: positions end at the opposite
      entry. REVERSAL INTENDED. No sizing code. FREQ = "2h" from the backtest header (UTC-aligned 2-hour
      bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI threshold crossings gated by latched divergences.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458252_rsi_threshold_cross_latched_divergence_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [14, 7],
    "xbars": [90, 45],
}
DEFAULT_PARAMS = {"len": 14, "xbars": 90, "buy_th": 30, "sell_th": 70}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["len"]))
    xb = int(p["xbars"])
    rv, cv = r.to_numpy(dtype=float), c.to_numpy(dtype=float)
    with np.errstate(invalid="ignore"):
        at_hi = rv >= r.rolling(xb).max().to_numpy()
        at_lo = rv <= r.rolling(xb).min().to_numpy()
    m = len(cv)
    mx, mxr, mn, mnr = (np.full(m, np.nan) for _ in range(4))
    bull, bear = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    divbull = divbear = False
    for i in range(m):
        pm, pmr = (mx[i - 1], mxr[i - 1]) if i > 0 else (np.nan, np.nan)
        qm, qmr = (mn[i - 1], mnr[i - 1]) if i > 0 else (np.nan, np.nan)
        a = cv[i] if at_hi[i] or np.isnan(pm) else pm
        ar = rv[i] if at_hi[i] or np.isnan(pmr) else pmr
        b = cv[i] if at_lo[i] or np.isnan(qm) else qm
        br = rv[i] if at_lo[i] or np.isnan(qmr) else qmr
        if cv[i] > a:
            a = cv[i]
        if rv[i] > ar:
            ar = rv[i]
        if cv[i] < b:
            b = cv[i]
        if rv[i] < br:
            br = rv[i]
        mx[i], mxr[i], mn[i], mnr[i] = a, ar, b, br
        if i >= 2:
            if mx[i - 1] > mx[i - 2] and rv[i - 1] < ar and rv[i] <= rv[i - 1]:
                divbear = True
            if mn[i - 1] < mn[i - 2] and rv[i - 1] > br and rv[i] >= rv[i - 1]:
                divbull = True
        bull[i], bear[i] = divbull, divbear
    bt, st = float(p["buy_th"]), float(p["sell_th"])
    le = pd.Series(bull, index=c.index) & (r > bt) & (r.shift(1) <= bt)
    se = pd.Series(bear, index=c.index) & (r < st) & (r.shift(1) >= st)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
