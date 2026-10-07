"""Pivot Point SuperTrend (LonesomeTheBlue): an ATR band around a running centre of confirmed
pivots; trend up-flip long, down-flip short (always in).
Port of FMZ strategy #363829 "Pivot Point SuperTrend".

Source
    https://www.fmz.com/strategy/363829 (PineScript v4, FMZ last modified 2022-05-17 16:03:36).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 53-123), pivot period 3, ATR factor 2, ATR period 6
    lastpp = pivothigh(3, 3) or pivotlow(3, 3); center := na(center) ? lastpp : (2 center + lastpp) / 3
    Up = center - 2 * atr(6); Dn = center + 2 * atr(6)
    TUp := close[1] > TUp[1] ? max(Up, TUp[1]) : Up;  TDown mirrors
    Trend := close > TDown[1] ? 1 : close < TUp[1] ? -1 : Trend[1] (1 at start)
    up-flip -> entry long; else down-flip -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pivots are confirmed 3 bars after the pivot bar (no look-ahead). A pivot value of 0 counts
      as no pivot (Pine float-as-bool), as coded.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_363829_pivot_point_supertrend"
FAMILY = "supertrend"  # proposed 2026-10-07, user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "prd": [2, 3, 5],
    "factor": [2.0, 3.0],
    "atr_period": [6, 10],
}
DEFAULT_PARAMS = {"prd": 3, "factor": 2.0, "atr_period": 6}


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


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


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


def _pivot_trend(bars, prd, factor, atr_p):
    h, l, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    ph = _pivots(bars["high"], prd, prd, True)
    pl = _pivots(bars["low"], prd, prd, False)
    atr = _atr_pine(bars, atr_p).to_numpy()
    m = len(c)
    trend = np.zeros(m)
    center = np.nan
    t_up = t_dn = np.nan
    for i in range(m):
        last = ph[i] if not np.isnan(ph[i]) and ph[i] != 0 else (pl[i] if not np.isnan(pl[i]) and pl[i] != 0 else np.nan)
        if not np.isnan(last):
            center = last if np.isnan(center) else (center * 2 + last) / 3
        up, dn = center - factor * atr[i], center + factor * atr[i]
        new_up = max(up, t_up) if i and c[i - 1] > t_up else up
        new_dn = min(dn, t_dn) if i and c[i - 1] < t_dn else dn
        prev = trend[i - 1] if i else 1.0
        trend[i] = 1.0 if c[i] > t_dn else (-1.0 if c[i] < t_up else prev)
        t_up, t_dn = new_up, new_dn
    return trend


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
    tr = _pivot_trend(bars_df, int(p["prd"]), float(p["factor"]), int(p["atr_period"]))
    prev = np.concatenate([[np.nan], tr[:-1]])
    return _always_in((tr == 1) & (prev == -1), (tr == -1) & (prev == 1), bars_df.index)


def portfolio_kwargs(**params):
    return {}
