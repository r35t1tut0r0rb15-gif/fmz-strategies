"""SMA 50 side with two-bar confirmation, 1-hour bars: on the second bar above the SMA 50, a green bar closing higher after
a green bar goes long; on the second bar below it, the mirror goes short; a close on the other side closes the
position.
Port of FMZ strategy #430549 "Dual Moving Average Crossover Scalping Strategy" (MovingAvg Cross).

FMZ source id: 430549

Source
    https://www.fmz.com/strategy/430549 (PineScript v4, FMZ last modified 2023-10-30 11:19:48).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 140-177), SMA 50, confirm bars 2
    bcount = bars in a row with close > sma50; scount = bars in a row with close < sma50
    close > close[1] and close > open and close[1] > open[1] and bcount == 2 -> entry long
    close < close[1] and close < open and close[1] < open[1] and scount == 2 -> entry short
    close < sma50 -> close long;  close > sma50 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries and closes exclude each other (a long entry needs the close above the SMA, which
      is the short's close condition, so an entry while short reverses it).
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a moving average and bar colours.
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

NAME = "fmz_430549_sma_side_confirm_bars"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 20, 100],
    "confirm_bars": [2, 3],
}
DEFAULT_PARAMS = {"length": 50, "confirm_bars": 2}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _run_count(cond):
    out = np.zeros(len(cond), dtype=np.int64)
    k = 0
    for i in range(len(cond)):
        k = k + 1 if cond[i] else 0
        out[i] = k
    return out


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
    ma = c.rolling(int(p["length"])).mean()
    bc, sc = (c > ma).to_numpy(), (c < ma).to_numpy()
    bcount, scount = _run_count(bc), _run_count(sc)
    nb = int(p["confirm_bars"])
    up = ((c > c.shift(1)) & (c > o) & (c.shift(1) > o.shift(1))).to_numpy() & (bcount == nb)
    dn = ((c < c.shift(1)) & (c < o) & (c.shift(1) < o.shift(1))).to_numpy() & (scount == nb)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        elif pos == 1 and sc[i]:
            pos = 0
        elif pos == -1 and bc[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
