"""EMA stack with CCI 200, 2-hour bars: the EMA 10 above the EMA 21 and EMA 50 with the CCI 200 above zero goes long, the mirror short; the EMA 10 crossing back through the EMA 21 closes.
Port of FMZ strategy #440550 "基于CCI和EMA的短线震荡策略CCI-and-EMA-Based-Scalping-Strategy" (EMA-CCI-strat).

FMZ source id: 440550

Source
    https://www.fmz.com/strategy/440550 (PineScript v3, FMZ last modified 2024-01-31 16:01:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 144-186), EMA 10 / 21 / 50 (exponential on); CCI 200; the tick exits are commented out
    buy_cond = ma10 > ma21 and ma10 > ma50 and cci(close, 200) > 0 -> entry Long;  ma10 < ma21 -> close Long;  sell_cond mirrored -> entry Short;  ma10 > ma21 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are levels; the take-profit / stop / trail exits are commented out, so the inputs
      are unused. The calls run in the written order: a long closed on a bar that also enters short
      becomes short. Pine's cci divides by 0.015 x the mean absolute deviation. strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. FREQ = "2h" from the backtest header (bars on UTC multiples of 2
      hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA stack and CCI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_440550_ema_stack_cci200"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cci_len": [200, 100],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"cci_len": 200, "slow": 50, "fast": 10, "mid": 21}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e10, e21, e50 = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("fast", "mid", "slow"))
    n = int(p["cci_len"])
    ma = c.rolling(n).mean()
    md = c.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    cci = (c - ma) / (0.015 * md.where(md > 0))
    buy = ((e10 > e21) & (e10 > e50) & (cci > 0)).to_numpy()
    sell = ((e10 < e21) & (e10 < e50) & (cci < 0)).to_numpy()
    xl, xs = (e10 < e21).to_numpy(), (e10 > e21).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i]:
            new = 1
        if xl[i] and pos == 1 and new == 1:
            new = 0
        if sell[i]:
            new = -1
        if xs[i] and pos == -1 and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
