"""Bollinger rebound, long only: the close crossing back above the lower band (SMA 20 -/+ 2 stdev 20)
goes long; a close at or above the upper band closes the long.
Port of FMZ strategy #427264 "Bollinger Bands Breakout Strategy".

FMZ source id: 427264

Source
    https://www.fmz.com/strategy/427264 (PineScript v4, FMZ last modified 2023-09-19 16:06:56).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 202-251), SMA 20, stdev 20, offsets 2.0 / 2.0
    crossover(close, sma - 2 stdev) and testPeriod() -> entry long ("CALL")
    close >= sma + 2 stdev -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * testPeriod() (2010-01-01 to 2030-12-30) is the author's backtest window: dropped.
    * stdev is the population standard deviation (Pine). Entries only from flat; one signal per bar.
    * FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bands in standard deviations.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427264_bb_ots_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_length": [20, 40],
    "lb_offset": [2.0, 2.5],
    "ub_offset": [2.0, 1.0],
}
DEFAULT_PARAMS = {"sma_length": 20, "std_length": 20, "lb_offset": 2.0, "ub_offset": 2.0}


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
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    mid = c.rolling(int(p["sma_length"])).mean()
    sd = c.rolling(int(p["std_length"])).std(ddof=0)
    lower, upper = mid - sd * p["lb_offset"], mid + sd * p["ub_offset"]
    entry = ((c > lower) & (c.shift(1) <= lower.shift(1))).to_numpy()
    exit_ = (c >= upper).to_numpy()
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
