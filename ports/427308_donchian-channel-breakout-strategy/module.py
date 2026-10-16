"""Donchian close breakout, long only: a close at or above the highest close of the previous 20 bars
goes long; a close below the channel middle closes the long.
Port of FMZ strategy #427308 "Donchian Channel Breakout Strategy".

FMZ source id: 427308

Source
    https://www.fmz.com/strategy/427308 (PineScript v3, FMZ last modified 2023-09-19 21:47:41).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 183-217), period 20
    upper = highest(close, 20)[1]; lower = lowest(close, 20)[1]; mid = (upper + lower) / 2
    close >= upper -> entry long; close < mid -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The channel covers the 20 closes before the current bar ([1]).
    * testPeriod() is the constant true. Long only; entries only from flat; one signal per bar.
    * FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bar counts only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, per-contract commission stored in original_sizing.txt.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: ND427308 (3 members, best partner #443123, Jaccard 0.790); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427308_donchian_close_breakout_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [20, 10, 55],
}
DEFAULT_PARAMS = {"period": 20}


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


def simulate(bars_df, **params):
    n = int({**DEFAULT_PARAMS, **params}["period"])
    c = bars_df["close"]
    up = c.rolling(n).max().shift(1)
    lo = c.rolling(n).min().shift(1)
    mid = (up + lo) / 2
    entry, exit_ = (c >= up).to_numpy(), (c < mid).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and entry[i]:
            le[i], pos = True, 1
        elif pos == 1 and exit_[i]:
            lx[i], pos = True, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
