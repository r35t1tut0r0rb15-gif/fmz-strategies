"""Regular RSI 60 (on ohlc4) divergences at pivots, 1-hour bars: a bullish divergence (price lower low, RSI higher low at 5 / 5 pivots 5-60 bars apart) with the RSI under 40 goes long, a bearish one with the RSI over 60 goes short; reversing. The average-price bracket is armed only by repeat signals and is not ported (pending).
Port of FMZ strategy #455354 "高级RSI背离与均线组合的量化交易策略-Advanced-Quantitative-Trading-Strategy-Combining-RSI-Divergence-and-Moving-Averages" (Advanced Gold Scalping Strategy with RSI Divergence).

FMZ source id: 455354

Source
    https://www.fmz.com/strategy/455354 (PineScript v5, FMZ last modified 2024-06-28 15:02:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 201-282), RSI 60 of ohlc4 (hand rma, 100 / 0 guards); pivots 5 / 5; range 5-60 bars; SL / TP 11 / 33 pips x 0.1 from the average price
    plFound = pivotlow(rsi, 5, 5);  rsi[5] > valuewhen(plFound, rsi[5], 1) and barssince(plFound[1]) in 5..60 and low[5] < valuewhen(plFound, low[5], 1) -> bullish;  bullish and rsi < 40 -> entry Long, exit(avg -+ 1.1 / 3.3)
    the mirror on pivot highs and rsi > 60 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The divergence follows the TradingView RSI divergence template as written (pivots strict on both
      sides, house helper). The exit is sent only on a signal bar, from the average price, which is
      na while flat: the opening signal arms nothing and a bracket appears only on a repeat signal
      inside the trade; stops() cannot express this, so it is not ported and the module is marked
      trailing_stop_pending (as #437800); positions end at the opposite entry. REVERSAL INTENDED. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the late-armed bracket pending (mark).
    2 generic: PASS, regular RSI divergences at pivots.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the pip bracket quoted.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_455354_rsi60_pivot_divergence_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [60, 14],
    "pivot": [5, 3],
}
DEFAULT_PARAMS = {"rsi_len": 60, "pivot": 5, "range_lo": 5, "range_hi": 60}


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


def _pivots(x, lb, rb, high):
    """True at bar t when bar t - rb is a strict pivot over lb bars before and rb bars after."""
    m = len(x)
    out = np.zeros(m, dtype=bool)
    for t in range(lb + rb, m):
        j = t - rb
        v = x[j]
        if np.isnan(v):
            continue
        left, right = x[j - lb:j], x[j + 1:t + 1]
        if np.isnan(left).any() or np.isnan(right).any():
            continue
        if high:
            out[t] = v > left.max() and v > right.max()
        else:
            out[t] = v < left.min() and v < right.min()
    return out


def _prev_value(found, src):
    """valuewhen(found, src, 1): src at the second most recent bar where found held."""
    out = np.full(len(src), np.nan)
    last = prev = np.nan
    for i in range(len(src)):
        if found[i]:
            prev, last = last, src[i]
        out[i] = prev
    return out


def _bars_since(ev):
    out = np.full(len(ev), np.nan)
    last = -1
    for i in range(len(ev)):
        if ev[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = (o + h + lo + c) / 4
    n = int(p["rsi_len"])
    d = src.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        raw = 100 - 100 / (1 + up / dn)
    rsi = raw.mask(up == 0, 0.0).mask(dn == 0, 100.0).where(up.notna() & dn.notna())
    k = int(p["pivot"])
    rv = rsi.to_numpy()
    pl, ph = _pivots(rv, k, k, False), _pivots(rv, k, k, True)
    r_k, lo_k, hi_k = rsi.shift(k).to_numpy(), lo.shift(k).to_numpy(), h.shift(k).to_numpy()
    pl1 = np.concatenate(([False], pl[:-1]))
    ph1 = np.concatenate(([False], ph[:-1]))
    bl, bh = _bars_since(pl1), _bars_since(ph1)
    a, b = int(p["range_lo"]), int(p["range_hi"])
    with np.errstate(invalid="ignore"):
        in_l = (bl >= a) & (bl <= b)
        in_h = (bh >= a) & (bh <= b)
        bull = (r_k > _prev_value(pl, r_k)) & in_l & (lo_k < _prev_value(pl, lo_k)) & pl
        bear = (r_k < _prev_value(ph, r_k)) & in_h & (hi_k > _prev_value(ph, hi_k)) & ph
        le = bull & (rv < 40)
        se = bear & (rv > 60)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
