"""Hidden RSI 14 divergences at 5 / 5 pivots (5-60 bars apart), 2-hour bars: a higher price low with a lower RSI low goes long, otherwise a lower price high with a higher RSI high goes short; reversing.
Port of FMZ strategy #362083 "TMA Legacy" (TMA-Legacy).

FMZ source id: 362083

Source
    https://www.fmz.com/strategy/362083 (PineScript v5, FMZ last modified 2022-05-09 22:59:36).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 84-378), RSI 14 (RSI Divergence display); pivots 5 / 5; range 5-60 bars
    plFound = pivotlow(rsi, 5, 5) found;  hiddenBull = low[5] > valuewhen(plFound, low[5], 1) and rsi[5] < valuewhen(plFound, rsi[5], 1) and 5 <= barssince(plFound[1]) <= 60 and plFound
    hiddenBear mirror on pivothigh(rsi, 5, 5) with high[5];  hiddenBull -> entry Long;  else hiddenBear -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * An indicator() script sending strategy orders on FMZ; the display menu takes its default (RSI
      Divergence: osc = RSI 14 of the close). The moving-average menu's VWMA / VWAP choices are not
      selected (SMMA is fixed), so volume is not used. valuewhen(cond, x, 1) is the value at the previous
      pivot; barssince is counted on plFound[1], as written; the pivots are strict on both sides (as
      #478737). REVERSAL INTENDED. No sizing code. The source carries the Mozilla Public License 2.0
      notice. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, hidden RSI divergences at pivots.
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

NAME = "fmz_362083_rsi14_hidden_divergence_pivot5_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [14, 21],
    "lb": [5, 3],
}
DEFAULT_PARAMS = {"rsi_length": 14, "lb": 5, "range_lower": 5, "range_upper": 60}


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


def _pivot(x, side, span=5):
    """Strict pivot of x at t - span, confirmed at t (Pine ta.pivothigh / pivotlow), on rolling
    windows: the centre beats every bar of the span on each side."""
    s = x if side > 0 else -x
    centre = s.shift(span)
    left = s.shift(span + 1).rolling(span).max()
    right = s.rolling(span).max()
    return ((centre > left) & (centre > right)).to_numpy()


def _valuewhen(cond, val, k):
    """Pine ta.valuewhen(cond, val, k): val at the k-th most recent bar where cond held (k = 0 latest)."""
    cond = np.asarray(cond, dtype=bool)
    val = np.asarray(val, dtype=float)
    out = np.full(len(cond), np.nan)
    hits = []
    for i in range(len(cond)):
        if cond[i]:
            hits.append(val[i])
        if len(hits) > k:
            out[i] = hits[-1 - k]
    return out


def _barssince(cond):
    """Pine ta.barssince: bars since cond was last true (NaN before the first true)."""
    a = np.asarray(cond, dtype=bool)
    idx = np.maximum.accumulate(np.where(a, np.arange(len(a)), -1))
    return np.where(idx >= 0, np.arange(len(a)) - idx, np.nan)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    lb = int(p["lb"])
    osc = _rsi(c, int(p["rsi_length"]))
    pl, ph = _pivot(osc, -1, lb), _pivot(osc, 1, lb)
    o_lb = osc.shift(lb).to_numpy(dtype=float)
    lo_lb, hi_lb = lo.shift(lb).to_numpy(dtype=float), h.shift(lb).to_numpy(dtype=float)
    rl, ru = int(p["range_lower"]), int(p["range_upper"])
    bs_l = _barssince(np.r_[False, pl[:-1]])
    bs_h = _barssince(np.r_[False, ph[:-1]])
    in_l = (rl <= bs_l) & (bs_l <= ru)
    in_h = (rl <= bs_h) & (bs_h <= ru)
    hid_bull = pl & (lo_lb > _valuewhen(pl, lo_lb, 1)) & (o_lb < _valuewhen(pl, o_lb, 1)) & in_l
    hid_bear = ph & (hi_lb < _valuewhen(ph, hi_lb, 1)) & (o_lb > _valuewhen(ph, o_lb, 1)) & in_h
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(hid_bull, index=ix), false, pd.Series(hid_bear & ~hid_bull, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
