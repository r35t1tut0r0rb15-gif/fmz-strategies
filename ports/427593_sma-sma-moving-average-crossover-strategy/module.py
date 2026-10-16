"""MA crossover: SMA 10 crossing above SMA 100 goes long, crossing below goes short (always in the
market after the first cross).
Port of FMZ strategy #427593 "SMA Moving Average Crossover Strategy".

FMZ source id: 427593

Source
    https://www.fmz.com/strategy/427593 (PineScript v3, FMZ last modified 2023-09-22 14:40:03).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 154-186), MA 10 SMA, MA 100 SMA
    price = security(ticker, timeframe.period, close) = close
    crossover(ma1, ma2) -> entry long; crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * security on the chart's own period is the series itself.
    * `ma_type` 1 = SMA for both (the defaults), 2 = EMA for both.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "6h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427593_sma_10_100_cross"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "6h"  # backtest header period: 6h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1": [10, 20],
    "ma2": [100, 50],
    "ma_type": [1, 2],
}
DEFAULT_PARAMS = {"ma1": 10, "ma2": 100, "ma_type": 1}


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
    c = bars_df["close"]
    if int(p["ma_type"]) == 2:
        a = c.ewm(span=int(p["ma1"]), adjust=False).mean()
        b = c.ewm(span=int(p["ma2"]), adjust=False).mean()
    else:
        a, b = c.rolling(int(p["ma1"])).mean(), c.rolling(int(p["ma2"])).mean()
    up = ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    dn = ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()
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
