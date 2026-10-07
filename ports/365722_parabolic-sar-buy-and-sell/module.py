"""Parabolic SAR side flips (start 0.00252, step 0.00133, max 0.22): SAR moving below the close
goes long, above goes short (always in).
Port of FMZ strategy #365722 "Parabolic SAR" (PSAR Buy and Sell Alerts).

Source
    https://www.fmz.com/strategy/365722 (PineScript v2/v3 syntax, FMZ last modified 2022-05-25 18:23:13).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 45-73)
    psar = sar(0.00252, 0.00133, 0.22);  dir = psar < close ? 1 : -1
    dir -1 -> 1 -> entry long; else dir 1 -> -1 -> entry short   ("Highlight Start Points" on)

Interpretation choices (Pine rules in SURVEY_README.md)
    * sar() as TradingView documents it (pine_sar helper, as in #362178).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "15min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365722_psar_side_flip"
FAMILY = "parabolic_sar"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "start": [0.00252, 0.02],
    "increment": [0.00133, 0.02],
    "maximum": [0.2, 0.22],
}
DEFAULT_PARAMS = {"start": 0.00252, "increment": 0.00133, "maximum": 0.22}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _sar_pine(bars, start, inc, maximum):
    """ta.sar as TradingView documents it (pine_sar): starts on bar 1, direction from close vs
    the previous close; value capped by the previous two bars' lows (highs)."""
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    out = np.full(m, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, m):
        first = False
        if i == 1:
            if c[1] > c[0]:
                below, max_min, result = True, h[1], lo[0]
            else:
                below, max_min, result = False, lo[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if below:
            if result > lo[i]:
                first, below = True, False
                result, max_min, acc = max(h[i], max_min), lo[i], start
        else:
            if result < h[i]:
                first, below = True, True
                result, max_min, acc = min(lo[i], max_min), h[i], start
        if not first:
            if below and h[i] > max_min:
                max_min, acc = h[i], min(acc + inc, maximum)
            elif (not below) and lo[i] < max_min:
                max_min, acc = lo[i], min(acc + inc, maximum)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return pd.Series(out, index=bars.index)


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
    psar = _sar_pine(bars_df, float(p["start"]), float(p["increment"]), float(p["maximum"]))
    c = bars_df["close"].to_numpy(dtype=float)
    d = np.where(psar < c, 1, -1)
    prev = np.concatenate([[0], d[:-1]])
    return _always_in((d == 1) & (prev == -1), (d == -1) & (prev == 1), bars_df.index)


def portfolio_kwargs(**params):
    return {}
