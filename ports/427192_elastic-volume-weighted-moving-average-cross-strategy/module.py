"""A 5-bar and a 40-bar elastic volume-weighted average of the close (each bar weighted by its share of the period's volume), 2-hour bars: the short one crossing over the long one goes long, crossing under goes short; reversing.
Port of FMZ strategy #427192 "Elastic Volume Weighted Moving Average Cross Strategy" (EVWMA Cross).

FMZ source id: 427192

Source
    https://www.fmz.com/strategy/427192 (PineScript v2, FMZ last modified 2023-09-18 22:08:05).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 210-231), EVWMA 5 / 40 (volume sums 5 / 40)
    evwma = nz(evwma[1]) x (sum(volume, n) - volume) / sum(volume, n) + volume x close / sum(volume, n)
    crossover(m1, m2) -> entry MA2CrossLE;  crossunder(m1, m2) -> entry MA2CrossSE

Interpretation choices (Pine rules in SURVEY_README.md)
    * The averages start from nz(data[1]) = 0 (Pine v2), so they climb from zero over the first bars, as
      written. REVERSAL INTENDED. No sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, elastic volume-weighted average cross.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the EVWMA weights and the rolling volume sums; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427192_evwma5_40_cross_reversal"
FAMILY = "volume_weighted_ma"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length1": [5, 10],
    "length2": [40, 20],
}
DEFAULT_PARAMS = {"length1": 5, "length2": 40}


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


def _evwma(c, v, n):
    """The source's calc_evwma: nz(prev) x (nb - v) / nb + v x close / nb, nb = sum(v, n)."""
    nb = v.rolling(n).sum().to_numpy(dtype=float)
    cv, vv = c.to_numpy(dtype=float), v.to_numpy(dtype=float)
    out = np.full(len(cv), np.nan)
    prev = 0.0
    for i in range(len(cv)):
        if nb[i] != 0:
            out[i] = prev * (nb[i] - vv[i]) / nb[i] + vv[i] * cv[i] / nb[i]
        prev = 0.0 if np.isnan(out[i]) else out[i]
    return pd.Series(out, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    m1, m2 = _evwma(c, v, int(p["length1"])), _evwma(c, v, int(p["length2"]))
    le = (m1 > m2) & (m1.shift(1) <= m2.shift(1))
    se = (m1 < m2) & (m1.shift(1) >= m2.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se & ~le, false.copy()


def portfolio_kwargs(**params):
    return {}
