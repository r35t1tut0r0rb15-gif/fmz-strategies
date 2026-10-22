"""2/20 EMA and Bill Williams three-lines combo, 1-hour bars: long when the EMA 14 band state and the displaced hl2 SMA 13 / 8 / 5 stack are both up, short when both are down, flat when they disagree.
Port of FMZ strategy #440110 "双移动平均线与Williams平均线组合策略Dual-Moving-Average-and-Williams-Average-Combination-Strategy" (Combo 2/20 EMA & Bill Williams Averages. 3Lines).

FMZ source id: 440110

Source
    https://www.fmz.com/strategy/440110 (PineScript v5, FMZ last modified 2024-01-26 16:36:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 157-207), EMA length 14; 3Lines 13 / 8 / 5 with offsets 8 / 5 / 3; reverse off; start 2005
    EMA20: xXA = ema(close, 14);  nXS = (min(low, low[1]) > xXA or max(high, high[1]) < xXA) ? min low : max high;  pos = nXS > close[1] ? -1 : nXS < close[1] ? 1 : pos[1]
    3Lines: L = sma(hl2, 13)[8], M = sma(hl2, 8)[5], S = sma(hl2, 5)[3];  pos = close < S < M < L ? -1 : close > S > M > L ? 1 : pos[1];  both 1 -> entry Long, both -1 -> entry Short, otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The displacements are lags of the averages (past values). The states are levels; disagreement
      closes. The 2005 start date is dropped. strategy.entry reverses: REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA band test and displaced averages.
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

NAME = "fmz_440110_ema_2_20_bw_three_lines_combo"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 20],
    "l_length": [13, 21],
}
DEFAULT_PARAMS = {"length": 14, "l_length": 13, "m_length": 8, "s_length": 5, "l_offset": 8, "m_offset": 5,
                  "s_offset": 3, "reverse": False}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    xa = c.ewm(span=int(p["length"]), adjust=False).mean()
    nhh = np.maximum(h, h.shift(1))
    nll = np.minimum(lo, lo.shift(1))
    nxs = nll.where((nll > xa) | (nhh < xa), nhh)
    c1 = c.shift(1)
    e_dn, e_up = (nxs > c1).to_numpy(), (nxs < c1).to_numpy()
    hl2 = (h + lo) / 2
    ls = hl2.rolling(int(p["l_length"])).mean().shift(int(p["l_offset"]))
    ms = hl2.rolling(int(p["m_length"])).mean().shift(int(p["m_offset"]))
    ss = hl2.rolling(int(p["s_length"])).mean().shift(int(p["s_offset"]))
    b_dn = ((c < ss) & (ss < ms) & (ms < ls)).to_numpy()
    b_up = ((c > ss) & (ss > ms) & (ms > ls)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pe = pb = 0
    for i in range(m):
        if e_dn[i]:
            pe = -1
        elif e_up[i]:
            pe = 1
        if b_dn[i]:
            pb = -1
        elif b_up[i]:
            pb = 1
        tgt[i] = 1 if (pe == 1 and pb == 1) else (-1 if (pe == -1 and pb == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
