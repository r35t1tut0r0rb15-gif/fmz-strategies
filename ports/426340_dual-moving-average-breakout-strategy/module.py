"""Noro's Multima: with the close above both SMA 40 and EMA 40, a red bar goes long; with the close
below both, a green bar goes short; when the two disagree the position is closed.
Port of FMZ strategy #426340 "Dual Moving Average Breakout Strategy".

Source
    https://www.fmz.com/strategy/426340 (PineScript v2, FMZ last modified 2023-09-11 12:31:51).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 75-93), SMA 40, EMA 40, colour filter on
    signal1 = close > sma(close, 40) ? 1 : -1;  signal2 = close > ema(close, 40) ? 1 : -1
    lots = signal1 + signal2
    lots > 0 and close < open -> entry long;  lots < 0 and close > open -> entry short
    lots == 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * While SMA 40 is na (first 39 bars) close > na is false, so signal1 = -1, as in Pine.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "10min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426340_noro_multima"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len_sma": [20, 40, 80],
    "len_ema": [20, 40, 80],
}
DEFAULT_PARAMS = {"len_sma": 40, "len_ema": 40}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(target, index):
    """Signals from the position each bar's orders leave (1 / 0 / -1): a change to +-1 is an
    entry (reversing an opposite position), a change to 0 an exit of the side held."""
    m = len(target)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    prev = 0
    for i in range(m):
        n = target[i]
        if n != prev:
            if n == 1:
                le[i] = True
            elif n == -1:
                se[i] = True
            elif prev == 1:
                lx[i] = True
            else:
                sx[i] = True
        prev = n
    return tuple(pd.Series(x, index=index) for x in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    s1 = np.where(c > c.rolling(int(p["len_sma"])).mean(), 1, -1)
    s2 = np.where(c > c.ewm(span=int(p["len_ema"]), adjust=False).mean(), 1, -1)
    lots = s1 + s2
    red, green = (c < o).to_numpy(), (c > o).to_numpy()
    target = np.zeros(len(c), dtype=int)
    pos = 0
    for i in range(len(c)):
        if lots[i] > 0 and red[i]:
            pos = 1
        elif lots[i] < 0 and green[i]:
            pos = -1
        elif lots[i] == 0:
            pos = 0
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
