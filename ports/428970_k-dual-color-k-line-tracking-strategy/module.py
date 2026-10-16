"""Noro candles, 2-hour bars: two red candles in a row go long, two green candles go short; any change of
candle colour closes the position.
Port of FMZ strategy #428970 "双色K线追踪策略Dual-Color-K-line-Tracking-Strategy" (Noro's Candles Strategy v1.0).

FMZ source id: 428970

Source
    https://www.fmz.com/strategy/428970 (PineScript v2, FMZ last modified 2023-10-11 14:53:41).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 165-195), bars Q 2
    bar = close > open ? 1 : close < open ? -1 : 0
    two red -> entry long; two green -> entry short; bar != bar[1] -> strategy.close_all()

Interpretation choices (Pine rules in SURVEY_README.md)
    * `time > timestamp(toyear 2018, ...)` is the author's backtest window: dropped (the colour-change
      exit is kept).
    * An entry bar always has bar == bar[1], so no close on an entry bar. A doji (bar 0) counts as a
      colour change. Opposite entries reverse: REVERSAL INTENDED. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle colours only.
    3 crypto-exchange-only: no (spot pair in the header only).
    4 signals only: the strategy() 100 % of equity stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428970_noro_candles"
FAMILY = "candle_pattern"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bq": [2, 3],
}
DEFAULT_PARAMS = {"bq": 2}


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
    bar = pd.Series(np.where(c > o, 1, np.where(c < o, -1, 0)), index=bars_df.index)
    n = int(p["bq"])
    red = (bar == -1).astype(float).rolling(n).min() == 1
    green = (bar == 1).astype(float).rolling(n).min() == 1
    change = (bar != bar.shift(1)) & bar.shift(1).notna()
    m = len(bar)
    up, dn, ex = red.to_numpy(), green.to_numpy(), change.to_numpy()
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        elif ex[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=idx)
    lx = pd.Series((prev == 1) & (tgt == 0), index=idx)
    se = pd.Series((tgt == -1) & (prev != -1), index=idx)
    sx = pd.Series((prev == -1) & (tgt == 0), index=idx)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
