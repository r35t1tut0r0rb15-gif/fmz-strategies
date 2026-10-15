"""HiLo: a close above the 4-bar SMA of highs goes long, a close below the 4-bar SMA of lows goes
short (always in the market after the first signal).
Port of FMZ strategy #427261 "Quantitative Trading Strategy Based on High-Low Point Moving Averages".

FMZ source id: 427261

Source
    https://www.fmz.com/strategy/427261 (PineScript v3, FMZ last modified 2023-09-19 15:53:55).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 163-197), length 4, displace 0
    close > sma(high, 4)[displace] -> entry long; close < sma(low, 4)[displace] -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * testPeriod() is defined (April 2017) but never used by the orders: no date filter, as written.
    * `displace` shifts the averages back (a lag of whole bars, >= 0): kept as a parameter.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_427261_hilo_sma_reversal"
FAMILY = "ma_envelope_breakout"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [4, 8, 16],
    "displace": [0, 1],
}
DEFAULT_PARAMS = {"length": 4, "displace": 0}


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
    n, k = int(p["length"]), int(p["displace"])
    c = bars_df["close"]
    hs = bars_df["high"].rolling(n).mean().shift(k)
    ls = bars_df["low"].rolling(n).mean().shift(k)
    long_c, short_c = (c > hs).to_numpy(), (c < ls).to_numpy()
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
