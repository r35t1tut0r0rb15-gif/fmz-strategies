"""Candle counter, 3-hour bars: over the current and previous 7 bars, more green bars than red bars holds a long,
otherwise a short; a red bar whose body is under a tiny fraction of the ATR counts as neutral.
Port of FMZ strategy #430164 "动态K线方向策略Dynamic-Candle-Direction-Strategy" (Refined CandleCounter Strategy by origo).

FMZ source id: 430164

Source
    https://www.fmz.com/strategy/430164 (PineScript v3, FMZ last modified 2023-10-25 16:57:05).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 159-195), 8 bars counted (i = 0 to 7)
    candle_dir = close > open ? 1 : round(close - open) == 0 ? 0 : -1
    indic = ups - dns; indic > 0 ? indic + neu : indic - neu
    indic > 0 -> entry long (qty 1);  indic <= 0 -> entry short (qty 1)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: round(close - open) == 0 is a price-unit test (a body under half a price unit);
      it becomes a body under doji_atr x Wilder ATR(14) of the same bar (0.002 ATR is about half a
      dollar on 3-hour BTC). Only non-green bars can be neutral, as written.
    * Adding or subtracting the neutral count never changes the sign of indic: the side is long
      exactly when the green bars outnumber the red ones, as written.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, the price-unit doji test -> an ATR fraction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: a fixed quantity of 1 stored in original_sizing.txt.
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

NAME = "fmz_430164_candle_counter"
FAMILY = "candle_pattern"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "num_candles": [7, 4],
    "doji_atr": [0.002, 0.05],
}
DEFAULT_PARAMS = {"num_candles": 7, "doji_atr": 0.002}


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
    o, c = bars_df["open"], bars_df["close"]
    doji = (c - o).abs() < p["doji_atr"] * _atr(bars_df, ATR_LEN)
    up = (c > o).astype(float)
    dn = ((c <= o) & ~doji).astype(float)
    w = int(p["num_candles"]) + 1
    ups = up.rolling(w, min_periods=1).sum()
    dns = dn.rolling(w, min_periods=1).sum()
    tgt = np.where(ups > dns, 1, -1).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
