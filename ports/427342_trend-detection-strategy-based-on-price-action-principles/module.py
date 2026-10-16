"""Trend detect from candle closes: each bar is typed by where its close sits in its range (lowest
third = 1, middle = 2, top third = 3); the EMA 5 of the share of type-3 bars over the previous 34 bars
crossing above the EMA 5 of the share of type-1 bars goes long, crossing below goes short (always in
the market after the first cross).
Port of FMZ strategy #427342 "Trend Detection Strategy Based on Price Action Principles".

FMZ source id: 427342

Source
    https://www.fmz.com/strategy/427342 (PineScript v2, FMZ last modified 2023-09-20 11:11:46).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 181-225), length 34, EMA 5
    delt = high - close; height = high - low
    state = delt > 2/3 height ? 1 : delt > 1/3 height ? 2 : 3
    perc(s) = 100 x count(state[i] == s, i = 1..34) / 34
    rise = ema(perc(3), 5); fall = ema(perc(1), 5)
    crossover(rise, fall) -> entry long; crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The count covers the 34 bars BEFORE the current one (i = 1..34), as written.
    * num / len x 100 is read as a real division (a share in percent). If Pine v2 divided the two
      integers as integers the share would be 0 or 100 only (decision owed if so).
    * A bar with no range (high == low) is type 3 (delt 0), as written.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, shares of candle types (dimensionless).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427342_close_position_trend_detect"
FAMILY = "candle_pattern"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [34, 21, 55],
    "ema_smooth": [5, 3],
}
DEFAULT_PARAMS = {"length": 34, "ema_smooth": 5}


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
    n, s = int(p["length"]), int(p["ema_smooth"])
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    delt, height = h - c, h - lo
    state = pd.Series(np.where(delt > height / 3 * 2, 1, np.where(delt > height / 3, 2, 3)), index=c.index)
    prev = state.shift(1)
    p3 = (prev == 3).astype(float).rolling(n).sum() / n * 100
    p1 = (prev == 1).astype(float).rolling(n).sum() / n * 100
    p3[prev.rolling(n).count() < n] = np.nan
    p1[prev.rolling(n).count() < n] = np.nan
    rise = p3.ewm(span=s, adjust=False).mean()
    fall = p1.ewm(span=s, adjust=False).mean()
    up = ((rise > fall) & (rise.shift(1) <= fall.shift(1))).to_numpy()
    dn = ((rise < fall) & (rise.shift(1) >= fall.shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
