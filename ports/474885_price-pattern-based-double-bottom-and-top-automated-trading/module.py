"""Exact double bottoms and tops, 3-minute bars: a bar making the 100-bar low at exactly the low of the previous bar that made it goes long, the mirror on the 100-bar high goes short; reversing. The close tests can never hold, as written.
Port of FMZ strategy #474885 "Price Pattern Based Double Bottom and Top Automated Trading Strategy" (Double Bottom and Top Hunter).

FMZ source id: 474885

Source
    https://www.fmz.com/strategy/474885 (PineScript v5, FMZ last modified 2024-12-12 17:29:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-148), length 100; lookback 100; qty 1
    low1 = lowest(low, 100);  low2 = valuewhen(low == low1, low, 1);  low == low1 and lowest(low, 100) == low1 and low == low2 -> entry Long;  mirror -> entry Short;  highest(high, 100) > high1 and low < low1 -> close Long (never true);  mirror -> close Short (never true)

Interpretation choices (Pine rules in SURVEY_README.md)
    * low2 is the low of the previous bar whose low was its 100-bar low, so the entry needs an exact
      repeat of that price. The close tests compare a series with itself (highest(high, 100) > high1)
      and never hold, so positions end at the opposite entry. REVERSAL INTENDED. The fixed qty is not
      ported. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, exact double bottoms / tops.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: fixed qty 1 stored, not ported.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474885_exact_double_bottom_top_100bar_reversal"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [100, 50],
}
DEFAULT_PARAMS = {"length": 100}


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


def _prev_when(values, hit):
    """ta.valuewhen(hit, values, 1): the value at the previous bar where hit held."""
    v = np.asarray(values, dtype=float)
    out = np.full(len(v), np.nan)
    last = prev = np.nan
    for i in range(len(v)):
        if hit[i]:
            prev, last = last, v[i]
        out[i] = prev
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo = bars_df["high"], bars_df["low"]
    n = int(p["length"])
    l1, h1 = lo.rolling(n).min(), h.rolling(n).max()
    at_low = (lo == l1).to_numpy()
    at_high = (h == h1).to_numpy()
    l2 = _prev_when(lo, at_low)
    h2 = _prev_when(h, at_high)
    lv, hv = lo.to_numpy(dtype=float), h.to_numpy(dtype=float)
    le = pd.Series(at_low & (lv == l2), index=bars_df.index)
    se = pd.Series(at_high & (hv == h2), index=bars_df.index)
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
