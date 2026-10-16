"""Triple cross on one bar, long only, 4-hour bars: go long when the stochastic K crosses above D and
EMA 5 and EMA 15 both cross above EMA 50 on the same bar; close when all three cross down together.
Port of FMZ strategy #427933 "4-Hour Stochastic EMA Trend Strategy" ("HelloWord").

FMZ source id: 427933

Source
    https://www.fmz.com/strategy/427933 (PineScript v4, FMZ last modified 2023-09-26 20:57:59).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 159-182), EMAs 5 / 15 / 50, stoch 13 / K 5 / D 15 (hard-coded)
    buy = crossover(k, d) and crossover(ema5, ema50) and crossover(ema15, ema50) -> entry long
    sell = crossunder(k, d) and crossunder(ema5, ema50) and crossunder(ema15, ema50) -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lengths are hard-coded in the source; the grid varies two of them.
    * Long only. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA and oscillator lengths only.
    3 crypto-exchange-only: no (spot pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427933_triple_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period3": [50, 30],
    "period_k": [13, 9],
}
DEFAULT_PARAMS = {"period1": 5, "period2": 15, "period3": 50, "period_k": 13, "period_d": 15, "smooth_k": 5}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e = lambda n: c.ewm(span=int(n), adjust=False).mean()
    m1, m2, m3 = e(p["period1"]), e(p["period2"]), e(p["period3"])
    n = int(p["period_k"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["period_d"])).mean()
    xo = lambda a, b: (a > b) & (a.shift(1) <= b.shift(1))
    xu = lambda a, b: (a < b) & (a.shift(1) >= b.shift(1))
    buy = (xo(k, d) & xo(m1, m3) & xo(m2, m3)).to_numpy()
    sell = (xu(k, d) & xu(m1, m3) & xu(m2, m3)).to_numpy()
    m = len(buy)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if buy[i]:
            pos = 1
        elif pos == 1 and sell[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
