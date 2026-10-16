"""Volatility breakout, 1-hour bars: the close crossing above the previous bar's high plus its ATR 20 goes long (when not
long), crossing below the previous bar's low minus its ATR goes short (when not short).
Port of FMZ strategy #430592 "Volatility Breakout Trading Strategy" (Volatility Breakout Strategy [Angel Algo]).

FMZ source id: 430592

Source
    https://www.fmz.com/strategy/430592 (PineScript v5, FMZ last modified 2023-10-30 16:58:03).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 132-177), ATR 20
    upper = high + atr(20); lower = low - atr(20)
    crossover(close, upper[1]) and position <= 0 -> entry long;  crossunder(close, lower[1]) and position >= 0 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * barstate.isconfirmed is true on every historical bar. The position tests only block same-side
      repeats (which the engine ignores anyway).
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430592_volatility_breakout_atr"
FAMILY = "atr_band_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 10, 40],
}
DEFAULT_PARAMS = {"length": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _atr(bars, n):
    c1 = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - c1).abs(), (bars["low"] - c1).abs()],
                   axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    a = _atr(bars_df, int(p["length"]))
    up1, dn1 = (h + a).shift(1), (lo - a).shift(1)
    xo = ((c > up1) & (c.shift(1) <= up1.shift(1))).to_numpy()
    xu = ((c < dn1) & (c.shift(1) >= dn1.shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if xo[i] and pos <= 0:
            pos = 1
        elif xu[i] and pos >= 0:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
