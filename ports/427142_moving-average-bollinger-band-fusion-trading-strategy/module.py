"""MA-Zorrillo: an SMA 8 / SMA 89 golden cross goes long if the close crossed back above the lower
Bollinger band (24, 2) within the last 64 bars; a death cross goes short if the close crossed
under the upper band within the last 64 bars (each entry closes the opposite side).
Port of FMZ strategy #427142 "Moving Average Bollinger Band Fusion Trading Strategy".

FMZ source id: 427142

Source
    https://www.fmz.com/strategy/427142 (PineScript v2, FMZ last modified 2023-09-18 16:08:43).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 109-147)
    entry = crossover(sma(close, 8), sma(close, 89)) and crossover(close, BB lower) on any of bars 0..63 back
    exit  = crossunder(sma 8, sma 89) and crossunder(close, BB upper) on any of bars 0..63 back
    entry -> long (and close short); exit -> short (and close long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The loop `for i = 0 to 63` includes the current bar: a 64-bar window ending at the bar.
    * The long close and the short entry fire on the same condition (and mirror): a one-bar
      reversal, REVERSAL INTENDED.
    * stdev is the population standard deviation (Pine). BB multiplier 2 is a constant.
    * FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths and a band in standard deviations.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: DG427142 (2 members, with #434978, Jaccard 0.952); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427142_ma_zorrillo"
FAMILY = "ma_trend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_long": [89, 55],
    "bb_length": [24, 20],
    "lookback": [64, 32],
}
DEFAULT_PARAMS = {"ma_short": 8, "ma_long": 89, "bb_length": 24, "bb_mult": 2.0, "lookback": 64}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _cross_over(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ms, ml = c.rolling(int(p["ma_short"])).mean(), c.rolling(int(p["ma_long"])).mean()
    n = int(p["bb_length"])
    basis, dev = c.rolling(n).mean(), p["bb_mult"] * c.rolling(n).std(ddof=0)
    entry_bb = _cross_over(c, basis - dev)
    exit_bb = _cross_over(basis + dev, c)
    k = int(p["lookback"])
    vs_entry = entry_bb.astype(float).rolling(k, min_periods=1).max() > 0
    vs_exit = exit_bb.astype(float).rolling(k, min_periods=1).max() > 0
    long_c = (_cross_over(ms, ml) & vs_entry).to_numpy()
    short_c = (_cross_over(ml, ms) & vs_exit).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i] and pos != 1:
            pos = 1
        elif short_c[i] and pos != -1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
