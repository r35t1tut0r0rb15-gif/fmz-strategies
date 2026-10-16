"""Weekly EMAs mapped to 3-hour bars: EMA 42 crossing above EMA 84, or EMA 84 crossing above EMA 182,
goes long; the matching down-crosses go short (the source's "Exit" orders are short entries).
Port of FMZ strategy #427398 "Daily Trading Strategy Based on Weekly EMAs".

FMZ source id: 427398

Source
    https://www.fmz.com/strategy/427398 (PineScript v1, FMZ last modified 2023-09-20 17:11:52).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 198-243), EMA 42 / 84 / 182, pyramiding 100
    enterLong1 = cross(ema42, ema84) and ema42 > ema84; exitLong1 = cross and ema42 < ema84
    enterLong2 = cross(ema84, ema182) and ema84 > ema182; exitLong2 = cross and ema84 < ema182
    strategy.entry("Entry_1"/"Entry_2", long = true); strategy.entry("Exit_1"/"Exit_2", long = false)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "Exit" ids are strategy.entry(long = false): SHORT entries that reverse the whole long
      position, as written (not plain closes). A second same-direction entry is an add (pyramiding
      100: sizing, stored); the net position follows the last signal's side: REVERSAL INTENDED.
    * On a bar with both a long and a short signal the short wins (it is placed last in the script).
    * window() is the constant true. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 100 stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427398_weekly_emas_on_3h"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [42, 21],
    "mid": [84, 63],
    "slow": [182, 126],
}
DEFAULT_PARAMS = {"fast": 42, "mid": 84, "slow": 182}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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
    e1, e2, e3 = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("fast", "mid", "slow"))

    def crossed(a, b):
        return ((a > b) & (a.shift(1) <= b.shift(1))) | ((a < b) & (a.shift(1) >= b.shift(1)))

    x12, x23 = crossed(e1, e2), crossed(e2, e3)
    long_c = ((x12 & (e1 > e2)) | (x23 & (e2 > e3))).to_numpy()
    short_c = ((x12 & (e1 < e2)) | (x23 & (e2 < e3))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if short_c[i]:
            pos = -1
        elif long_c[i]:
            pos = 1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
