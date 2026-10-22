"""Donchian closing breakouts, 1-hour bars: a close equal to the 50-bar highest close goes long, equal to the 50-bar lowest close goes short; reversing (the small channel is also 50 bars, so the Donchian
exit coincides with the opposite entry).
Port of FMZ strategy #440557 "Donchian Trend Following Strategy" (Donchian).

FMZ source id: 440557

Source
    https://www.fmz.com/strategy/440557 (PineScript v5, FMZ last modified 2024-01-31 16:53:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 160-294), length 50/50; long and short on; risk 0.5 %, ATR 20 x 2 (stop off); close in end on (window always true)
    position <= 0 and close == highest(close, 50) -> entry Long (risk-sized qty);  position >= 0 and close == lowest(close, 50) -> entry Short
    position > 0 and close == lowest(close, 50) -> close Long;  position < 0 and close == highest(close, 50) -> close Short;  (stop orders only with "Permit stop", off)

Interpretation choices (Pine rules in SURVEY_README.md)
    * With "50/50" the exit channel equals the entry channel, so a Donchian close comes on the same bar
      as the opposite entry and the reversal stands (as #438020). The risk-based quantity, capital,
      per-order commission and slippage are sizing and costs; the stop block (with its openprofit move
      to break-even) is off. The trade window is always true. REVERSAL INTENDED. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, closing-price channel.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: risk-sized quantity, capital, commission and slippage settings.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG440557 (2 members, best partner #439623, Jaccard 0.899); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440557_donchian_close_channel_reversal"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "big": [50, 20],
    "small": [50, 10],
}
DEFAULT_PARAMS = {"big": 50, "small": 50}


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
    nb, ns = int(p["big"]), int(p["small"])
    L = (c == c.rolling(nb).max()).to_numpy()
    S = (c == c.rolling(nb).min()).to_numpy()
    LX = (c == c.rolling(ns).min()).to_numpy()
    SX = (c == c.rolling(ns).max()).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if L[i] and pos <= 0:
            new = 1
        if S[i] and pos >= 0:
            new = -1
        if LX[i] and pos == 1 and new == 1:
            new = 0
        if SX[i] and pos == -1 and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
