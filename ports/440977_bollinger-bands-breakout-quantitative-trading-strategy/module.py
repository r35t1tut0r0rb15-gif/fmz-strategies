"""Bollinger band breakouts, 1-hour bars: the close crossing over the upper band (60, 2) goes long, under the lower band short; the close crossing back under the upper (or lower) band closes a long,
back over the lower (or upper) band closes a short; reversing.
Port of FMZ strategy #440977 "Bollinger Bands Breakout Quantitative Trading Strategy" (Fuera Bolinga).

FMZ source id: 440977

Source
    https://www.fmz.com/strategy/440977 (PineScript v5, FMZ last modified 2024-02-04 14:52:52).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 132-171), BB 60 / 2; take profit 6 % and stop 1.5 % declared but unused
    crossover(close, upper) -> entry BBandLE (else cancel);  crossunder(close, lower) -> entry BBandSE (else cancel)
    (crossunder(close, upper) or crossunder(close, lower)) and in a trade -> close BBandLE;  (crossover(close, lower) or crossover(close, upper)) and in a trade -> close BBandSE

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cancel calls act on market entries that have already filled and do nothing. The closes act
      only on the held position; a close written after a reversing entry leaves the reversal standing (as
      #438020). The take-profit and stop percentages are never used. Pine's stdev is the population
      deviation. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger band crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_440977_bollinger_breakout_band_return_exit"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [60, 20],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 60, "mult": 2.0}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, lo = basis + dev, basis - dev

    def xo(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    L, S = xo(c, up).to_numpy(), xo(lo, c).to_numpy()
    XL = (xo(up, c) | xo(lo, c)).to_numpy()
    XS = (xo(c, lo) | xo(c, up)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if L[i]:
            new = 1
        if S[i]:
            new = -1
        if XL[i] and pos == 1 and new == 1:
            new = 0
        if XS[i] and pos == -1 and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
