"""Combo 2/20 EMA & APO (HPotter): long when both the 2/20 EMA state and the APO (EMA 10 - EMA 20)
state are +1, short when both are -1, flat otherwise.
Port of FMZ strategy #426377 "Dual Moving Average Indicators Fusion Strategy".

Source
    https://www.fmz.com/strategy/426377 (PineScript v5, FMZ last modified 2023-09-11 16:32:22).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 92-138), Length 14, APO 10 / 20
    xXA = ema(close, 14); nHH = max(high, high[1]); nLL = min(low, low[1])
    nXS = (nLL > xXA or nHH < xXA) ? nLL : nHH
    posEMA = nXS > close[1] ? -1 : nXS < close[1] ? 1 : previous
    posAPO = apo > 0 ? 1 : apo < 0 ? -1 : previous
    both +1 -> entry long; both -1 -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The first bar's nHH / nLL are na (high[1] na), so the state keeps its previous value.
    * "Trade reverse" off (source default); the start date (2005) is a backtest window.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "12h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426377_combo_2_20_ema_apo"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "12h"  # backtest header period: 12h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 20],
    "apo_short": [10],
    "apo_long": [20, 30],
}
DEFAULT_PARAMS = {"length": 14, "apo_short": 10, "apo_long": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _state(up, dn):
    out = np.zeros(len(up))
    prev = 0.0
    for i in range(len(up)):
        prev = -1.0 if dn[i] else (1.0 if up[i] else prev)
        out[i] = prev
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ema = lambda n: c.ewm(span=int(n), adjust=False).mean()
    xa = ema(p["length"])
    hh = pd.concat([h, h.shift(1)], axis=1).max(axis=1, skipna=False)
    ll = pd.concat([l, l.shift(1)], axis=1).min(axis=1, skipna=False)
    xs = ll.where((ll > xa) | (hh < xa), hh)
    c1 = c.shift(1)
    a = _state((xs < c1).to_numpy(), (xs > c1).to_numpy())
    apo = ema(p["apo_short"]) - ema(p["apo_long"])
    b = _state((apo > 0).to_numpy(), (apo < 0).to_numpy())
    target = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0))
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
