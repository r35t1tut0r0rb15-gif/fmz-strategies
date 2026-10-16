"""Noro's Bollinger v1.0, mean reversion: a close under the lower band (SMA 20 -/+ 1 stdev) goes
long, a close over the upper band goes short; a long is closed on the first green bar, a short on
the first red bar.
Port of FMZ strategy #427440 "Bollinger Breakout Strategy".

FMZ source id: 427440

Source
    https://www.fmz.com/strategy/427440 (PineScript v2, FMZ last modified 2023-09-21 10:38:13).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 140-172), length 20, mult 1.0, both sides on, pyramiding 5
    close < lower -> entry long; close > upper -> entry short
    (long and close > open) or (short and close < open) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md; Noro's template as worker A's ports)
    * pyramiding 5 adds are sizing (stored); one position.
    * The year window (1900-2100) and its close_all are the author's backtest window: dropped.
    * An entry and the close_all on one bar: the entry is taken (the close tests the position held
      before the bar's orders); strategy.entry reverses: REVERSAL INTENDED.
    * stdev is the population standard deviation. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bands in standard deviations, candle colours.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, pyramiding 5 stored in original_sizing.txt.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427440_noro_bollinger_fade"
FAMILY = "bollinger_reversion"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40, 10],
    "mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 1.0}


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
    c, o = bars_df["close"], bars_df["open"]
    n = int(p["length"])
    basis, dev = c.rolling(n).mean(), p["mult"] * c.rolling(n).std(ddof=0)
    up = (c < basis - dev).to_numpy()
    dn = (c > basis + dev).to_numpy()
    green, red = (c > o).to_numpy(), (c < o).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i] and pos != 1:
            pos = 1
        elif dn[i] and pos != -1:
            pos = -1
        elif (pos == 1 and green[i]) or (pos == -1 and red[i]):
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
