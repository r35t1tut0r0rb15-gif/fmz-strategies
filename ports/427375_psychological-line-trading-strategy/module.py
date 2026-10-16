"""Psychological line (HPotter): the share of up-closes over the last 20 bars above 50 % goes long,
below 50 % goes short (always in the market after the first signal).
Port of FMZ strategy #427375 "Psychological Line Trading Strategy".

FMZ source id: 427375

Source
    https://www.fmz.com/strategy/427375 (PineScript v2, FMZ last modified 2023-09-20 14:50:47).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 160-172), length 20, reverse off
    psy = 100 x sum(close > close[1], 20) / 20
    pos = psy > 50 ? 1 : psy < 50 ? -1 : pos[1] -> entries on pos

Interpretation choices (Pine rules in SURVEY_README.md)
    * The window includes the current bar; the first bar's comparison with na counts as false.
    * strategy.entry reverses: REVERSAL INTENDED; "Trade reverse" is off.
    * FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a share of up-closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427375_psychological_line"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 12, 40],
}
DEFAULT_PARAMS = {"length": 20}


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
    n = int({**DEFAULT_PARAMS, **params}["length"])
    c = bars_df["close"]
    psy = ((c > c.shift(1)).astype(float).rolling(n).sum() / n * 100).to_numpy()
    m = len(psy)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if psy[i] > 50:
            pos = 1
        elif psy[i] < 50:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
