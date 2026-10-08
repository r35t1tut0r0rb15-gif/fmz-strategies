"""Parabolic SAR on close (QuantNomad, always in): the SAR flips when a close crosses it; a flip to
up goes long, to down goes short.
Port of FMZ strategy #426993 "Parabolic SAR Trailing Stop Loss Strategy".

Source
    https://www.fmz.com/strategy/426993 (PineScript v4, FMZ last modified 2023-09-16 18:54:28).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 125-168), 0.02 / 0.02 / 0.2
    long_to_short = dir[1] == 1 and close <= psar[1];  short_to_long mirrors
    dir: second bar from its first candle's colour; flips set it; else nz(dir[1])
    af / ep / psar: the classic recursion on high / low (start, increment, maximum)
    short_to_long -> entry long;  long_to_short -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The first bar's values are na; the SAR starts on the second bar (barstate.isfirst[1]).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "3h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426993_psar_on_close"
FAMILY = "parabolic_sar"  # proposed 2026-10-07, user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "start": [0.01, 0.02],
    "increment": [0.01, 0.02],
    "maximum": [0.2],
}
DEFAULT_PARAMS = {"start": 0.02, "increment": 0.02, "maximum": 0.2}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, l, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    nan = np.nan
    psar_p, af_p, dir_p, ep_p = nan, nan, nan, nan
    for i in range(m):
        first_prev = i == 1
        l2s = dir_p == 1 and c[i] <= psar_p
        s2l = dir_p == -1 and c[i] >= psar_p
        change = first_prev or l2s or s2l
        if first_prev:
            d = 1 if c[i - 1] > o[i - 1] else -1
        elif l2s:
            d = -1
        elif s2l:
            d = 1
        else:
            d = 0 if np.isnan(dir_p) else dir_p
        if change:
            af = p["start"]
        elif (d == 1 and h[i] > ep_p) or (d == -1 and l[i] < ep_p):
            af = min(p["maximum"], af_p + p["increment"])
        else:
            af = af_p
        if change and d == 1:
            ep = h[i]
        elif change and d == -1:
            ep = l[i]
        elif d == 1:
            ep = max(ep_p, h[i]) if not np.isnan(ep_p) else nan
        else:
            ep = min(ep_p, l[i]) if not np.isnan(ep_p) else nan
        if first_prev:
            ps = l[i - 1] if c[i - 1] > o[i - 1] else h[i - 1]
        elif change:
            ps = ep_p
        elif d == 1:
            ps = psar_p + af * (ep - psar_p)
        else:
            ps = psar_p - af * (psar_p - ep)
        le[i], se[i] = s2l, l2s
        psar_p, af_p, dir_p, ep_p = ps, af, d, ep
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
