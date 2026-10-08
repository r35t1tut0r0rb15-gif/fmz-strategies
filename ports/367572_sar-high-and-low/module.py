"""SAR high and low (Zer3192): the Parabolic SAR crossing above the lower band of a 40-bar EMA +- 2 sd
envelope of itself goes long; crossing below the upper band goes short (always in).
Port of FMZ strategy #367572 "SAR -high and low".

Source
    https://www.fmz.com/strategy/367572 (PineScript v4, author Zer3192, FMZ last modified
    2022-06-04 08:50:51). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 39-75), SAR 0.02 / 0.02 / 0.2, look-back 40, multiplier 2
    s1 = sar(0.02, 0.02, 0.2);  mean = ema(s1, 40);  sd = 2 * stdev(s1, 40)
    crossover(s1, mean - sd) -> entry long; else crossunder(s1, mean + sd) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * sar() as TradingView documents it (pine_sar). Population stdev.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_367572_sar_envelope_cross"
FAMILY = "parabolic_sar"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "look_back": [20, 40],
    "multi": [1.0, 2.0],
}
DEFAULT_PARAMS = {"start": 0.02, "increment": 0.02, "maximum": 0.2, "look_back": 40, "multi": 2.0}


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
    s1 = pd.Series(_sar_pine(bars_df, p["start"], p["increment"], p["maximum"]), index=bars_df.index)
    n = int(p["look_back"])
    mean, sd = s1.ewm(span=n, adjust=False).mean(), p["multi"] * s1.rolling(n).std(ddof=0)
    lo, up = mean - sd, mean + sd
    buy = ((s1 > lo) & (s1.shift(1) <= lo.shift(1))).to_numpy()
    sell = ((s1 < up) & (s1.shift(1) >= up.shift(1))).to_numpy()
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
