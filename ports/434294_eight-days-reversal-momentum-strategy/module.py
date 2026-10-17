"""Raschke-style eight-bar runs, 1-hour bars: after at least 8 bars without a close under the SMA 5, the first close at or
under it goes long, closed when a close is back above it; after 8 bars without a close above the SMA 5, the first close
at or above it goes short, closed when a close is back under it.
Port of FMZ strategy #434294 "Eight Days Reversal Momentum Strategy" (8D Run).

FMZ source id: 434294

Source
    https://www.fmz.com/strategy/434294 (PineScript v5, FMZ last modified 2023-12-05 10:56:37).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 117-148), SMA 5, run length 8
    TriggerBuy = barssince(close < sma5) >= 8;  Buy = TriggerBuy[1] and close <= sma5 -> entry long;  close > sma5 -> close long
    TriggerSell = barssince(close > sma5) >= 8;  Sell = TriggerSell[1] and close >= sma5 -> entry short;  close < sma5 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * barssince is na until the condition has occurred once (no trigger before that). The closes act
      on the position held on the bar; an entry on the same bar wins (the short entry is issued
      last), and strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, runs against a short average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() capital and commission stored.
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

NAME = "fmz_434294_eight_bar_run_reversal"
FAMILY = "ma_pullback"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [5, 10],
    "run": [8, 5],
}
DEFAULT_PARAMS = {"sma_len": 5, "run": 8}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _barssince(cond):
    m = len(cond)
    out = np.full(m, np.nan)
    last = -1
    for i in range(m):
        if cond[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    sma = c.rolling(int(p["sma_len"])).mean()
    cv, sv = c.to_numpy(dtype=float), sma.to_numpy(dtype=float)
    n = int(p["run"])
    with np.errstate(invalid="ignore"):
        tb = _barssince(cv < sv) >= n
        ts = _barssince(cv > sv) >= n
        tb1 = np.concatenate(([False], tb[:-1]))
        ts1 = np.concatenate(([False], ts[:-1]))
        buy = tb1 & (cv <= sv)
        sell = ts1 & (cv >= sv)
        above, below = cv > sv, cv < sv
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if pos == 1 and above[i]:
            new = 0
        if pos == -1 and below[i]:
            new = 0
        if buy[i]:
            new = 1
        if sell[i]:
            new = -1
        tgt[i] = new
        pos = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
