"""Regular divergences between price and a five-stage colour-signed volume average (WMA 5 / 8 / 13 / 21 / 34, each bar's volume negative on down bars) at 5 / 5 pivots 5-60 bars apart, 30-minute bars: a lower price low with a higher volume low goes long, otherwise a higher price high with a lower volume high goes short; reversing.
Port of FMZ strategy #365895 "Volume Divergence" (Volume Divergence by MM).

FMZ source id: 365895

Source
    https://www.fmz.com/strategy/365895 (PineScript v4, FMZ last modified 2022-05-26 17:04:32).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 52-237), WMA 5 / 8 / 13 / 21 / 34 (signed by candle colour); pivots 5 / 5; range 5-60; regular divergences only (hidden off)
    pine_wma(x, y) = sum(x[i] (y - i) y f[i]) / sum((y - i) y), f = -1 on down bars;  vol = pine_wma(pine_wma(... pine_wma(volume, 5) ..., 21), 34)
    bull = low[5] < valuewhen(pl, low[5], 1) and vol[5] > valuewhen(pl, vol[5], 1) and 5 <= barssince(pl[1]) <= 60 and pl -> entry Long;  else bear mirror -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A study() script sending strategy orders on FMZ. The source's pine_wma is a WMA of x times each bar's
      colour sign (the sign of the bar the value belongs to), applied at all five stages, as written. The
      hidden divergences are off by default. The pivots are strict on both sides (as #478737).
      REVERSAL INTENDED. No sizing code. The source carries the Mozilla Public License 2.0 notice.
      FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price / signed-volume divergences at pivots.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar), signed by candle colour and averaged in five WMA stages; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365895_signed_volume_wma_stack_regular_divergence_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vl1": [5, 8],
    "lb": [5, 3],
}
DEFAULT_PARAMS = {"vl1": 5, "vl2": 8, "lb": 5, "range_lower": 5, "range_upper": 60}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _wma(x, n):
    """Pine ta.wma over each n-bar window (NaN when the window holds a NaN)."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.arange(1, n + 1, dtype=float)              # newest bar weighted n
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def _pivot(x, side, span=5):
    """Strict pivot of x at t - span, confirmed at t (Pine ta.pivothigh / pivotlow), on rolling
    windows: the centre beats every bar of the span on each side."""
    s = x if side > 0 else -x
    centre = s.shift(span)
    left = s.shift(span + 1).rolling(span).max()
    right = s.rolling(span).max()
    return ((centre > left) & (centre > right)).to_numpy()


def _valuewhen(cond, val, k):
    """Pine valuewhen(cond, val, k): val at the k-th most recent bar where cond held (k = 0 latest)."""
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
    """Pine barssince: bars since cond was last true (NaN before the first true)."""
    a = np.asarray(cond, dtype=bool)
    idx = np.maximum.accumulate(np.where(a, np.arange(len(a)), -1))
    return np.where(idx >= 0, np.arange(len(a)) - idx, np.nan)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    f = pd.Series(np.where(c < o, -1.0, 1.0), index=c.index)
    a, b = int(p["vl1"]), int(p["vl2"])
    lengths = [a, b, a + b, b + (a + b), (a + b) + (b + a + b)]
    x = v
    for n in lengths:
        x = _wma(x * f, n)                          # pine_wma: each term signed by its bar's colour
    vol = x
    lb = int(p["lb"])
    pl, ph = _pivot(vol, -1, lb), _pivot(vol, 1, lb)
    v_lb = vol.shift(lb).to_numpy(dtype=float)
    lo_lb, hi_lb = lo.shift(lb).to_numpy(dtype=float), h.shift(lb).to_numpy(dtype=float)
    rl, ru = int(p["range_lower"]), int(p["range_upper"])
    bs_l, bs_h = _barssince(np.r_[False, pl[:-1]]), _barssince(np.r_[False, ph[:-1]])
    bull = pl & (lo_lb < _valuewhen(pl, lo_lb, 1)) & (v_lb > _valuewhen(pl, v_lb, 1)) & (rl <= bs_l) & (bs_l <= ru)
    bear = ph & (hi_lb > _valuewhen(ph, hi_lb, 1)) & (v_lb < _valuewhen(ph, v_lb, 1)) & (rl <= bs_h) & (bs_h <= ru)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(bull, index=ix), false, pd.Series(bear & ~bull, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
