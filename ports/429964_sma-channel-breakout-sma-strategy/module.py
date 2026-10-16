"""Channel breakout with an SMA 9 / 21 trend filter, 1-minute bars: a green bar touching the 7-bar high with SMA 9 above
SMA 21 goes long, a red bar touching the 7-bar low with SMA 9 below SMA 21 goes short; the SMAs crossing against the
position close it.
Port of FMZ strategy #429964 "双均线通道突破SMA策略Channel-Breakout-SMA-Strategy".

FMZ source id: 429964

Source
    https://www.fmz.com/strategy/429964 (PineScript v4, FMZ last modified 2023-10-23 17:08:51).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 140-173), channel 7, SMA 9 / 21
    long = (close >= highest(high,7) or high >= highest(high,7)) and sma9 > sma21 and close > open -> entry long
    short = (close <= lowest(low,7) or low <= lowest(low,7)) and sma9 < sma21 and close < open -> entry short
    crossunder(sma9, sma21) closes a long; crossover closes a short

Interpretation choices (Pine rules in SURVEY_README.md)
    * highest / lowest include the current bar (so the high test is "this bar made the 7-bar high").
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel touches and moving-average states.
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

NAME = "fmz_429964_channel_touch_sma_filter"
FAMILY = "donchian_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [7, 20],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"length": 7, "fast": 9, "slow": 21}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    ub, db = h.rolling(n).max(), lo.rolling(n).min()
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    lc = (((c >= ub) | (h >= ub)) & (f > s) & (c > o)).to_numpy()
    sc = (((c <= db) | (lo <= db)) & (f < s) & (c < o)).to_numpy()
    xl = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    xs = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        p0 = pos
        if lc[i]:
            pos = 1
        if sc[i]:
            pos = -1
        if p0 == 1 and pos == 1 and xl[i]:
            pos = 0
        if p0 == -1 and pos == -1 and xs[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
