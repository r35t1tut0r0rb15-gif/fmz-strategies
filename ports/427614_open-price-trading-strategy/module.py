"""Open / close ratio: when the average of open / close over the previous 9 bars is below 1 (the bars
closed up on average) go long, above 1 go short (always in the market).
Port of FMZ strategy #427614 "Open Price Trading Strategy" ("PerfectStrategy").

FMZ source id: 427614

Source
    https://www.fmz.com/strategy/427614 (PineScript v2, FMZ last modified 2023-09-22 17:00:25).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 160-179)
    y = mean of open[i] / close[i] for i = 1..9
    y < 1 -> entry long; y > 1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The current bar is not in the average (lags 1..9 as written); `n` is the count of lags.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price ratios only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored in original_sizing.txt.
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

NAME = "fmz_427614_open_close_ratio_mean"
FAMILY = "candle_pattern"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [9, 5, 15, 20],
}
DEFAULT_PARAMS = {"n": 9}


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
    ratio = bars_df["open"] / bars_df["close"]
    y = ratio.shift(1).rolling(int(p["n"])).mean().to_numpy()
    m = len(y)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if y[i] < 1:
            pos = 1
        elif y[i] > 1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
