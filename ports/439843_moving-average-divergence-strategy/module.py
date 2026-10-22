"""Regular and hidden divergences between price and a WMA 14, 1-hour bars: a pivot low of the WMA (5 / 5) where price and the WMA disagree with the previous pivot low (lower low / higher low or the reverse)
goes long; the mirror at pivot highs goes short; reversing.
Port of FMZ strategy #439843 "Moving Average Divergence Strategy" (MA Divergences).

FMZ source id: 439843

Source
    https://www.fmz.com/strategy/439843 (PineScript v4, FMZ last modified 2024-01-24 11:43:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 134-333), WMA 14 of close; pivots 5 / 5; range 2 to 600 bars; all four divergence kinds on; test period true
    plFound = pivotlow(osc, 5, 5) found;  oscHL = osc[5] > valuewhen(plFound, osc[5], 1) and inRange(plFound[1]);  priceLL = low[5] < valuewhen(plFound, low[5], 1)
    bull = priceLL and oscHL and plFound;  hidden bull = priceHL and oscLL and plFound;  bear / hidden bear at pivot highs;  entry Buy on bull or hidden bull, entry Sell on bear or hidden bear

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pivots are strict on both sides and known 5 bars after the pivot (#434470). valuewhen(..., 1) is
      the previous pivot's value. inRange(plFound[1]) counts the bars since the last pivot before the
      current bar; it must be 2 to 600. A pivot low and a pivot high cannot share a bar. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; pivots known after the right lookback.
    2 generic: PASS, WMA pivots and price pivots.
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

NAME = "fmz_439843_wma14_regular_hidden_divergence"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [14, 21],
    "lb": [5, 3],
}
DEFAULT_PARAMS = {"len": 14, "lb": 5, "range_lower": 2, "range_upper": 600}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _pivot(x, left, right, low):
    """True at bar i when bar i - right is a strict pivot (both sides), known at bar i."""
    m = len(x)
    out = np.zeros(m, dtype=bool)
    for i in range(left + right, m):
        p = i - right
        v = x[p]
        if np.isnan(v):
            continue
        w = np.concatenate((x[p - left:p], x[p + 1:i + 1]))
        if np.isnan(w).any():
            continue
        out[i] = (v < w).all() if low else (v > w).all()
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _div(found, osc_r, px_r, lo_side, rl, ru):
    """Regular / hidden divergence flags at pivot bars against the previous pivot."""
    m = len(found)
    reg, hid = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last_i, po, pp = -1, np.nan, np.nan
    for i in range(m):
        if found[i]:
            if last_i >= 0:
                bars = i - 1 - last_i                    # barssince(found[1]) at bar i
                ok = rl <= bars <= ru
                if lo_side:
                    reg[i] = ok and osc_r[i] > po and px_r[i] < pp
                    hid[i] = ok and osc_r[i] < po and px_r[i] > pp
                else:
                    reg[i] = ok and osc_r[i] < po and px_r[i] > pp
                    hid[i] = ok and osc_r[i] > po and px_r[i] < pp
            last_i, po, pp = i, osc_r[i], px_r[i]
    return reg | hid


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    osc = _wma(c, int(p["len"]))
    lb = int(p["lb"])
    ov = osc.to_numpy()
    pl, ph = _pivot(ov, lb, lb, True), _pivot(ov, lb, lb, False)
    o_r = osc.shift(lb).to_numpy()
    lo_r = bars_df["low"].shift(lb).to_numpy()
    hi_r = bars_df["high"].shift(lb).to_numpy()
    rl, ru = int(p["range_lower"]), int(p["range_upper"])
    buy = _div(pl, o_r, lo_r, True, rl, ru)
    sell = _div(ph, o_r, hi_r, False, rl, ru)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(buy & ~sell, index=ix), false, pd.Series(sell, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
