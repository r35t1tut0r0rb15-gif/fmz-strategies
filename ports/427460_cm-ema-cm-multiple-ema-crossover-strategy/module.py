"""CM EMA trend cross: EMA 21 crossing above EMA 55 with EMA 13 above EMA 55 goes long; EMA 21 crossing
below EMA 55 with EMA 13 below it goes short (always in the market after the first cross).
Port of FMZ strategy #427460 "CM Multiple EMA Crossover Strategy".

FMZ source id: 427460

Source
    https://www.fmz.com/strategy/427460 (PineScript v4, FMZ last modified 2023-09-21 12:12:56).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 151-180), EMA 8 / 13 / 21 / 55
    up = crossover(ema21, ema55) and ema8 and ema13 > ema55 -> entry long
    dn = crossunder(ema21, ema55) and ema8 and ema13 < ema55 -> entry short
    strategy.close("Close Long" / "Close Short", ...)

Interpretation choices (Pine rules in SURVEY_README.md)
    * `and ema8` tests the EMA as a boolean (true whenever it is not 0 / na): no filter on prices.
    * The closes name ids that no entry uses ("Close Long" / "Close Short"), so they never close
      anything: the only exit is the opposite entry. REVERSAL INTENDED.
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

NAME = "fmz_427460_cm_ema_trend_cross"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "6h"  # backtest header period: 6h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mid": [21, 13],
    "slow": [55, 89],
    "filt": [13, 8],
}
DEFAULT_PARAMS = {"mid": 21, "slow": 55, "filt": 13}


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
    e_mid, e_slow, e_f = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("mid", "slow", "filt"))
    up = ((e_mid > e_slow) & (e_mid.shift(1) <= e_slow.shift(1)) & (e_f > e_slow)).to_numpy()
    dn = ((e_mid < e_slow) & (e_mid.shift(1) >= e_slow.shift(1)) & (e_f < e_slow)).to_numpy()
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
