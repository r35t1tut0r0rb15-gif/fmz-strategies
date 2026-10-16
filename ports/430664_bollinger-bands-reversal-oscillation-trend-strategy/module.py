"""Bollinger band breakouts (gsanson66), 1-hour bars: a close above the upper band (20, 2) goes long, under the lower band
goes short; a close back across the SMA 20 closes the position.
Port of FMZ strategy #430664 "Bollinger Bands Reversal Oscillation Trend Strategy" (BOLLINGER BANDS BACKTESTING).

FMZ source id: 430664

Source
    https://www.fmz.com/strategy/430664 (PineScript v5, FMZ last modified 2023-10-31 14:30:45).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 183-279), BB 20 / 2, exit SMA 20, fixed-ratio money management
    long and close < sma(close, 20) -> close long;  short and close > sma -> close short     (written first)
    close > upperBB -> entry long (qty = cashOrder / close);  close < lowerBB -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes are written before the entries: a close and an opposite entry on one bar reverse
      the position. The fixed-ratio order sizing (cashOrder grows / shrinks in 200 $ steps per 400 $
      of equity) is sizing: stored, not ported.
    * The 2020-2024 range is unused (inRange = true). strategy.entry reverses: REVERSAL INTENDED.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands and a moving average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed-ratio cash sizing stored in original_sizing.txt.
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

NAME = "fmz_430664_bb_breakout_sma_exit"
FAMILY = "bollinger_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_length": [20, 50],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"bb_length": 20, "mult": 2.0, "sma_length": 20}


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
    n = int(p["bb_length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    up = (c > basis + p["mult"] * sd).to_numpy()
    dn = (c < basis - p["mult"] * sd).to_numpy()
    sma = c.rolling(int(p["sma_length"])).mean()
    below, above = (c < sma).to_numpy(), (c > sma).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 1 and below[i]:
            pos = 0
        elif pos == -1 and above[i]:
            pos = 0
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
