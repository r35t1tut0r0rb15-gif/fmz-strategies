"""Noro's triple RSI extremes, 1-minute bars: RSI 2 / 7 / 14 all deeply oversold (12 / 24 / 36) goes long, all overbought
(88 / 76 / 64) goes short; a green bar closes a long (the short exit is written as the long one, so shorts leave only by
reversal).
Port of FMZ strategy #430844 "三重RSI极值交易策略Triple-RSI-Extremum-Trading-Strategy" (Noro's Triple RSI Top/Bottom).

FMZ source id: 430844

Source
    https://www.fmz.com/strategy/430844 (PineScript v3, FMZ last modified 2023-11-02 14:34:21).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 140-190), RSI 2 / 7 / 14, accuracy 3 (acc = 7)
    up = rsi2 < 5 + acc and rsi7 < 10 + 2 acc and rsi14 < 15 + 3 acc -> (close a short) entry long
    dn = rsi2 > 95 - acc and rsi7 > 90 - 2 acc and rsi14 > 85 - 3 acc -> (close a long) entry short
    exit = (long and close > open) or (long and close > open) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit repeats the long test twice (no short exit), as written. close_all acts on the
      position held at the start of the bar: a green bar ends a held long (even on a bar that also
      signals); a short leaves only by the long signal.
    * RSIs are Wilder's (rma). The 1900-2100 window is the author's: dropped. strategy.entry
      reverses: REVERSAL INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and bar colour.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity per entry stored in original_sizing.txt.
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

NAME = "fmz_430844_noro_triple_rsi_extremes"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "accuracy": [3, 5, 1],
}
DEFAULT_PARAMS = {"accuracy": 3}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


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
    acc = 10 - int(p["accuracy"])
    r2, r7, r14 = _rsi(c, 2), _rsi(c, 7), _rsi(c, 14)
    up = ((r2 < 5 + acc) & (r7 < 10 + 2 * acc) & (r14 < 15 + 3 * acc)).to_numpy()
    dn = ((r2 > 95 - acc) & (r7 > 90 - 2 * acc) & (r14 > 85 - 3 * acc)).to_numpy()
    green = (c > o).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        if start == 1 and green[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
