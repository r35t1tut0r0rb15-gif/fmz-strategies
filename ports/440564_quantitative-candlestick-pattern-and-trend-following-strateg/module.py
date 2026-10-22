"""Turtle-style closing breakouts, 1-hour bars: a close above the previous 20-bar highest close goes long; a close at or under the previous 10-bar lowest close closes the long and goes short; a close
above the previous 10-bar highest close closes the short (the candle patterns are plotted only).
Port of FMZ strategy #440564 "Quantitative Candlestick Pattern and Trend Following Strategy" (TurtleBC-V.Troussel).

FMZ source id: 440564

Source
    https://www.fmz.com/strategy/440564 (PineScript v3, FMZ last modified 2024-01-31 17:24:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 224-453), enter 20, exit 10, short exit 10 (closes); doji 0.05; dates from 2016
    enterL1 = close > highest(close, 20)[1] -> entry Long;  exitL1 = close <= lowest(close, 10)[1] -> close Long and entry Short;  exitS = close > highest(close, 10)[1] -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The candle-pattern section only plots. The calls run in the written order: a long closed by
      exitL1 is replaced by the short entered on the same bar; a short close written after a long entry
      on the same bar leaves the long standing (as #438020). The date window is dropped. REVERSAL
      INTENDED. The capital is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, closing-price channels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: capital is sizing.
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

NAME = "fmz_440564_turtle_close_channel_long_short"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "enter_fast": [20, 55],
    "exit_fast": [10, 20],
}
DEFAULT_PARAMS = {"enter_fast": 20, "exit_fast": 10}


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
    ef, xf = int(p["enter_fast"]), int(p["exit_fast"])
    L = (c > c.rolling(ef).max().shift(1)).to_numpy()
    XL = (c <= c.rolling(xf).min().shift(1)).to_numpy()
    XS = (c > c.rolling(xf).max().shift(1)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if L[i]:
            new = 1
        if XL[i] and pos == 1 and new == 1:
            new = 0
        if XL[i]:
            new = -1
        if XS[i] and pos == -1 and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
