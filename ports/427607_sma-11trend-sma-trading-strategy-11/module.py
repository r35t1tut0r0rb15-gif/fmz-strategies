"""Noro's trend pullback: the trend is up once a bar's low clears EMA 15 and down once a bar's high is
below it; in an up trend a red bar dipping under EMA 5 goes long, in a down trend a green bar poking
over EMA 5 goes short.
Port of FMZ strategy #427607 "Trend SMA Trading Strategy 1.1".

FMZ source id: 427607

Source
    https://www.fmz.com/strategy/427607 (PineScript v2, FMZ last modified 2023-09-22 16:40:33).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 159-183), fast 5, slow 15
    fastsma = ema(close, 5); slowsma = ema(close, 15)   (named SMA, computed as EMA)
    trend = low > slowsma ? 1 : high < slowsma ? -1 : trend[1]
    up = trend == 1 and low < fastsma and close < open -> entry long
    dn = trend == -1 and high > fastsma and close > open -> entry short (qty 0 if "only long")

Interpretation choices (Pine rules in SURVEY_README.md)
    * The averages are EMAs as written (the titles say SMA).
    * "Only long?" (default false) sets the short quantity to 0: sizing; ported with the default
      (shorts at full size), so the strategy reverses: REVERSAL INTENDED.
    * trend[1] is na before the first defining bar (v2): no signal until then.
    * FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the only-long quantity stored in original_sizing.txt.
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

NAME = "fmz_427607_noro_trend_ema_pullback"
FAMILY = "ma_pullback"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fastlen": [5, 10],
    "slowlen": [15, 30],
}
DEFAULT_PARAMS = {"fastlen": 5, "slowlen": 15}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    fast = bars_df["close"].ewm(span=int(p["fastlen"]), adjust=False).mean().to_numpy()
    slow = bars_df["close"].ewm(span=int(p["slowlen"]), adjust=False).mean().to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    trend = 0          # 0 = na
    pos = 0
    for i in range(m):
        if lo[i] > slow[i]:
            trend = 1
        elif h[i] < slow[i]:
            trend = -1
        up = trend == 1 and lo[i] < fast[i] and c[i] < o[i]
        dn = trend == -1 and h[i] > fast[i] and c[i] > o[i]
        if up:
            pos = 1
        elif dn:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
