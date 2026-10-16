"""Chikou crossover: the Ichimoku base line (Donchian midpoint of 26 bars) crossing above the close of
26 bars ago goes long, crossing below goes short (always in the market after the first cross).
Port of FMZ strategy #427806 "Cloud Crossover Strategy Based on Market Momentum" ("Chikou Crossover").

FMZ source id: 427806

Source
    https://www.fmz.com/strategy/427806 (PineScript v3, FMZ last modified 2023-09-25 17:28:29).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 153-182), base line 26, lag 26 (hard-coded)
    baseLine = avg(lowest(26), highest(26))
    crossover(baseLine, close[26]) -> entry long; crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conversion line and the cloud are drawn only; the displacement input is unused by the
      orders (the lag 26 is written into the cross). `lag` is that hard-coded 26.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND427806 (2 members, best partner #429786, Jaccard 0.658); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427806_chikou_base_line_cross"
FAMILY = "ichimoku"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "base_periods": [26, 52],
    "lag": [26, 13],
}
DEFAULT_PARAMS = {"base_periods": 26, "lag": 26}


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
    n = int(p["base_periods"])
    base = (bars_df["low"].rolling(n).min() + bars_df["high"].rolling(n).max()) / 2
    lagged = bars_df["close"].shift(int(p["lag"]))
    up = ((base > lagged) & (base.shift(1) <= lagged.shift(1))).to_numpy()
    dn = ((base < lagged) & (base.shift(1) >= lagged.shift(1))).to_numpy()
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
