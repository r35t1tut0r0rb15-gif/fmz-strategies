"""HPotter's "DPO" state, 30-minute bars: the close above its SMA 14 turns the state long, below it short; always in the
state's direction.
Port of FMZ strategy #433079 "Detrended Price Oscillator Quantitative Trading Strategy" (Detrended Price Oscillator (HPotter)).

FMZ source id: 433079

Source
    https://www.fmz.com/strategy/433079 (PineScript v2, FMZ last modified 2023-11-24 11:22:30).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 123-138), length 14, price close, reverse false
    nRes = close - sma(close, 14);  pos = nRes > 0 ? 1 : nRes < 0 ? -1 : nz(pos[1], 0)
    pos 1 -> entry long;  pos -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "detrended price" here is the close minus its undisplaced SMA (no half-period shift), as
      written. The state holds at exactly zero. strategy.entry reverses: REVERSAL INTENDED. reverse is
      false. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, the close against its own average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: ND433079 (2 members, best partner #434175, Jaccard 0.670); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433079_close_vs_sma_state"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 28, 50],
}
DEFAULT_PARAMS = {"length": 14}


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
    res = (c - c.rolling(int(p["length"])).mean()).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if res[i] > 0:
            pos = 1
        elif res[i] < 0:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index)
                 for a in ((tgt == 1) & (prev != 1), false, (tgt == -1) & (prev != -1), false.copy()))


def portfolio_kwargs(**params):
    return {}
