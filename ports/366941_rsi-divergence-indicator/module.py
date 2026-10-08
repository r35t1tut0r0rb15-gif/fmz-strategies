"""RSI divergence indicator: a regular BEARISH RSI divergence (price higher high, RSI lower high on
confirmed pivots) goes LONG and a regular bullish one goes SHORT, as written (always in).
Port of FMZ strategy #366941 "RSI Divergence Indicator w/Alerts".

Source
    https://www.fmz.com/strategy/366941 (PineScript v4, FMZ last modified 2022-05-31 18:54:21).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 57-228), RSI 14 on close, pivots 5 / 5, range 5..60
    bullCond = low[5] < previous pivot-low low and osc[5] > previous pivot-low osc, in range
    bearCond = high[5] > previous pivot-high high and osc[5] < previous pivot-high osc, in range
    bearCond -> entry "Enter Long"; else bullCond -> entry "Enter Short"

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are inverted relative to the divergence names; kept as written.
    * Hidden divergences default off. Pivots confirmed 5 bars later (no look-ahead).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "5min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_366941_rsi_divergence_inverse"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [9, 14],
    "lb": [3, 5, 8],
}
DEFAULT_PARAMS = {"rsi_len": 14, "lb": 5, "range_lo": 5, "range_hi": 60}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(close, n):
    d = close.diff()
    return 100.0 - 100.0 / (1.0 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))


def _pivots(x, left, right, high):
    """ta.pivothigh/pivotlow(x, left, right): value of the pivot confirmed on each bar (NaN if
    none); the centre bar t-right strictly beyond the `left` bars before and `right` bars after."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    for t in range(left + right, len(v)):
        c = t - right
        side = np.concatenate([v[c - left:c], v[c + 1:t + 1]])
        if np.isnan(v[c]) or np.isnan(side).any():
            continue
        if (high and v[c] > side.max()) or (not high and v[c] < side.min()):
            out[t] = v[c]
    return out


def _divergence(osc, low, high, lb_l, lb_r, r_lo, r_hi):
    """TradingView "Divergence" template: regular bullish (price lower low, osc higher low) and
    bearish (price higher high, osc lower high) on pivots confirmed lb_r bars later; the previous
    pivot must be r_lo..r_hi bars back (barssince(found[1]))."""
    o = pd.Series(osc)
    pl = ~np.isnan(_pivots(o, lb_l, lb_r, False))
    ph = ~np.isnan(_pivots(o, lb_l, lb_r, True))
    o_r = o.shift(lb_r).to_numpy()
    lo_r = pd.Series(low).shift(lb_r).to_numpy()
    hi_r = pd.Series(high).shift(lb_r).to_numpy()
    m = len(o_r)
    bull, bear = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pl_last = ph_last = None  # (bar, osc, price) of the latest found pivot
    pl_prev = ph_prev = None  # the one before
    for i in range(m):
        # barssince(found[1]) uses pivots found up to bar i-1
        bs_pl = i - 1 - pl_last[0] if pl_last is not None else np.nan
        bs_ph = i - 1 - ph_last[0] if ph_last is not None else np.nan
        if pl[i]:
            pl_prev, pl_last = pl_last, (i, o_r[i], lo_r[i])
            if pl_prev is not None:
                bull[i] = (o_r[i] > pl_prev[1] and r_lo <= bs_pl <= r_hi and lo_r[i] < pl_prev[2])
        if ph[i]:
            ph_prev, ph_last = ph_last, (i, o_r[i], hi_r[i])
            if ph_prev is not None:
                bear[i] = (o_r[i] < ph_prev[1] and r_lo <= bs_ph <= r_hi and hi_r[i] > ph_prev[2])
    return bull, bear


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    osc = _rsi(bars_df["close"], int(p["rsi_len"])).to_numpy()
    k = int(p["lb"])
    bull, bear = _divergence(osc, bars_df["low"].to_numpy(), bars_df["high"].to_numpy(), k, k,
                             int(p["range_lo"]), int(p["range_hi"]))
    return _always_in(bear, bull, bars_df.index)


def portfolio_kwargs(**params):
    return {}
