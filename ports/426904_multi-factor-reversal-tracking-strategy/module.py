"""Combo 123 Reversal & reverse-engineered RSI (HPotter): long when the 123-reversal state and the
"price RSI(14) = 50 would need is below the close" state are both +1, short when both are -1,
flat otherwise.
Port of FMZ strategy #426904 "Multi factor Reversal Tracking Strategy".

Source
    https://www.fmz.com/strategy/426904 (PineScript v2/v3 syntax, FMZ last modified 2023-12-01 14:59:14).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 170-215), 14 / 1 / 3 / 50, Value 50, WildPer 14
    K = 2 / (2 * 14); AUC / ADC = EMA-style averages of gains / losses, seeded nz(..., 1)
    nVal = 13 (ADC * 50 / 50 - AUC); nRes = nVal >= 0 ? close + nVal : close + nVal * 50 / 50
    posRE = nRes > close ? -1 : nRes < close ? 1 : previous
    both +1 -> entry long; both -1 -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The averages start from 1 (nz(..., 1)), as written; the first bar's close[1] is na, so it
      counts as a loss bar. The -1 test comes first.
    * "Trade reverse" off. strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "2h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426904_combo_123_reversal_re_rsi"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21],
    "value": [50, 70],
    "wild_per": [14, 21],
}
DEFAULT_PARAMS = {"length": 14, "value": 50, "wild_per": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _state(up, dn):
    """HPotter state: +1 on up, -1 on dn (up tested first), else the previous value (0 at start)."""
    out = np.zeros(len(up))
    prev = 0.0
    for i in range(len(up)):
        prev = 1.0 if up[i] else (-1.0 if dn[i] else prev)
        out[i] = prev
    return out


def _pos_123(bars, length=14, k_smooth=1, d_length=3, level=50):
    """HPotter's 123 reversal state (stoch over a flat range is na)."""
    h, l, c = bars["high"], bars["low"], bars["close"]
    lo, hi = l.rolling(int(length)).min(), h.rolling(int(length)).max()
    fast = (100 * (c - lo) / (hi - lo)).rolling(int(k_smooth)).mean()
    slow = fast.rolling(int(d_length)).mean()
    c1, c2 = c.shift(1), c.shift(2)
    return _state(((c2 < c1) & (c > c1) & (fast < slow) & (fast > level)).to_numpy(),
                  ((c2 > c1) & (c < c1) & (fast > slow) & (fast < level)).to_numpy())


def _combo_target(a, b):
    return np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0))


def _emit(target, index):
    """Signals from the position each bar's orders leave (1 / 0 / -1): a change to +-1 is an
    entry (reversing an opposite position), a change to 0 an exit of the side held."""
    m = len(target)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    prev = 0
    for i in range(m):
        n = target[i]
        if n != prev:
            if n == 1:
                le[i] = True
            elif n == -1:
                se[i] = True
            elif prev == 1:
                lx[i] = True
            else:
                sx[i] = True
        prev = n
    return tuple(pd.Series(x, index=index) for x in (le, lx, se, sx))


def _re_rsi_state(close, value, wild):
    c = close.to_numpy(dtype=float)
    k = 2 / ((2 * wild - 1) + 1)
    auc = adc = np.nan
    out = np.zeros(len(c))
    prev = 0.0
    for i in range(len(c)):
        a1 = 1.0 if np.isnan(auc) else auc
        d1 = 1.0 if np.isnan(adc) else adc
        up = i > 0 and c[i] > c[i - 1]
        auc = k * (c[i] - c[i - 1]) + (1 - k) * a1 if up else (1 - k) * a1
        adc = (1 - k) * d1 if up else (k * (c[i - 1] - c[i]) + (1 - k) * d1 if i > 0 else np.nan)
        nval = (wild - 1) * (adc * value / (100 - value) - auc)
        res = c[i] + nval if nval >= 0 else c[i] + nval * (100 - value) / value
        if res > c[i]:
            prev = -1.0
        elif res < c[i]:
            prev = 1.0
        out[i] = prev
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _pos_123(bars_df, p["length"])
    b = _re_rsi_state(bars_df["close"], p["value"], p["wild_per"])
    return _emit(_combo_target(a, b), bars_df.index)


def portfolio_kwargs(**params):
    return {}
