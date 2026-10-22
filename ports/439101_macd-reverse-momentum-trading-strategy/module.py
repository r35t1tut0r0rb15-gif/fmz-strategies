"""Blau's Ergotic MACD state, 1-hour bars: EMA 32 minus EMA 5 under its EMA 5 signal holds a long, above it a short; reversing.
Port of FMZ strategy #439101 "基于改进型MACD指标的短线交易策略Reverse-Momentum-Trading-Strategy" (Ergotic MACD Strategy Backtest).

FMZ source id: 439101

Source
    https://www.fmz.com/strategy/439101 (PineScript v2, FMZ last modified 2024-01-17 17:29:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 166-182), r 32 (slow 5 fixed); SmthLen 5 (unused); reverse off
    xmacd = ema(close, 32) - ema(close, 5);  signal = ema(xmacd, 5);  pos = 1 if xmacd < signal, -1 if xmacd > signal, else pos[1];  entries by pos

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "MACD" is the slow EMA minus the fast one (Blau's inverted form), so the long side is xmacd under
      its signal, as written. The state is a level, so the entry is sent on every bar of the state.
      reverse is off. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, inverted MACD against its signal.
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

NAME = "fmz_439101_ergotic_macd_state"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "r": [32, 64],
    "fast": [5, 10],
}
DEFAULT_PARAMS = {"r": 32, "fast": 5, "signal": 5, "reverse": False}


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
    x = c.ewm(span=int(p["r"]), adjust=False).mean() - c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = x.ewm(span=int(p["signal"]), adjust=False).mean()
    a, b = x.to_numpy(), s.to_numpy()
    m = len(a)
    st = np.zeros(m)
    for i in range(m):
        prev = st[i - 1] if i > 0 else 0.0
        st[i] = 1.0 if a[i] < b[i] else (-1.0 if a[i] > b[i] else prev)
    if p["reverse"]:
        st = -st
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(st == 1, index=ix), false, pd.Series(st == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
