"""Bollinger %B extremes, 4-hour bars: from flat, %B below -0.2 goes long and above 1.2 goes short; a
long closes once %B is back to 0.2, a short once it is back to 1.0.
Port of FMZ strategy #427816 "BBB Strategy".

FMZ source id: 427816

Source
    https://www.fmz.com/strategy/427816 (PineScript v5, FMZ last modified 2023-09-25 17:53:36).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 185-216), SMA 21, 2 stdev, lines 1.2 / 1.0 / -0.2 / 0.2
    bbr = (close - lower) / (upper - lower)
    bbr < -0.2 and flat -> entry long; bbr >= 0.2 and long -> close_all
    bbr > 1.2 and flat -> entry short; bbr <= 1.0 and short -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() line is commented out: Pine defaults (one contract, one position).
    * Opposite entries cannot occur: entries need a flat position at the bar.
    * FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, %B levels only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427816_bollinger_pctb_extremes"
FAMILY = "mean_reversion_band"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 50],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 21, "mult": 2.0, "ob": 1.2, "ob_close": 1.0, "os": -0.2, "os_close": 0.2}


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
    n = int(p["length"])
    basis, dev = c.rolling(n).mean(), p["mult"] * c.rolling(n).std(ddof=0)
    bbr = ((c - (basis - dev)) / (2 * dev)).to_numpy()
    m = len(bbr)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if start == 0 and bbr[i] < p["os"]:
            pos = 1
        if start == 1 and bbr[i] >= p["os_close"]:
            pos = 0
        if start == 0 and bbr[i] > p["ob"]:
            pos = -1
        if start == -1 and bbr[i] <= p["ob_close"]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
