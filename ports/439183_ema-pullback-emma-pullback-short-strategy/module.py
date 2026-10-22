"""A one-way short after a close crossing over the EMA 50, 1-minute bars, short only: the close crossing over the EMA 50 on a green bar after a red one, with the close 3 bars ago above the one 2 bars ago, goes
short; the stop is gated on a long position and never sent, so the first short is held.
Port of FMZ strategy #439183 "基于EMA回调的Pullback空头策略Emma-Pullback-Short-Strategy" (EMA Pullback).

FMZ source id: 439183

Source
    https://www.fmz.com/strategy/439183 (PineScript v4, FMZ last modified 2024-01-18 11:02:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 122-165), EMA 50; pullback candles 3; engulfing candles 1; stop 1 ATR (14)
    bearish_impulse = crossover(close, ema 50);  pullback = close[3] > close[2] (the loop keeps the last test);  engulfing = close[1] < open[1] and close > open
    all three -> entry Short;  exit(stop = close + atr, when = position_size[1] > 0)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The loops overwrite their flag on every pass, so only the last test counts (as written). The exit is
      gated on position_size[1] > 0, which a short-only script never has, so no stop is placed and the
      first short is held to the end of the data, as written (owed: probably position_size < 0). Short
      only: Opposite entries cannot occur. No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossing and bar patterns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only: Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439183_ema_cross_short_held"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [50, 100],
    "pullback_candles": [3, 2],
}
DEFAULT_PARAMS = {"ema_length": 50, "pullback_candles": 3}


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
    o, c = bars_df["open"], bars_df["close"]
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    impulse = (c > e) & (c.shift(1) <= e.shift(1))
    k = int(p["pullback_candles"])
    pull = c.shift(k) > c.shift(k - 1)
    engulf = (c.shift(1) < o.shift(1)) & (c > o)
    sig = (impulse & pull & engulf).to_numpy()
    m = len(c)
    se = np.zeros(m, dtype=bool)
    hits = np.flatnonzero(sig[:-1]) if m > 1 else np.array([], dtype=int)
    if len(hits):
        se[hits[0]] = True                               # never closed: later shorts are ignored
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return false, false.copy(), pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
