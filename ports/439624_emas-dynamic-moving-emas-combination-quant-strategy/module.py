"""Full EMA-ladder breakouts, 1-hour bars: with the close above the EMA 3 and the EMAs 3 > 15 > 19 > 50 > 100 > 150 > 171 > 172 and a run of higher highs, the script goes long; the mirror goes short; the
four fast EMAs turning down (or the low crossing under all four) closes a long, the mirror closes a short.
Port of FMZ strategy #439624 "动态移动EMAS组合量化策略Dynamic-Moving-EMAs-Combination-Quant-Strategy" (Crypto MAX Trend).

FMZ source id: 439624

Source
    https://www.fmz.com/strategy/439624 (PineScript v4, FMZ last modified 2024-01-22 12:34:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 136-207), EMAs 3 / 15 / 19 / 50 / 100 / 150 / 171 / 172 of close; date window true
    long = close > ema3 and the ladder up and close > high[1] > high[2] and close > high[3], high[4], high[5] and high[5] > high[6];  short mirror with lows
    exitlong = ema3 < ema15 < ema19 < ema50 or (low crossing under ema3, 15, 19 and 50 on one bar);  exitshort mirror;  entry long / entry short, then close long / close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes come after the entries: a close of the side just reversed out of meets no position and
      the reversal stands (as #438020); from flat the entry opens; a held position meeting its close
      ends flat. A same-side entry while in the position is ignored. strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA ladder and high / low runs.
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

NAME = "fmz_439624_ema_ladder_breakout_crypto_max"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [3, 5],
    "length4": [50, 34],
}
DEFAULT_PARAMS = {"length": 3, "length4": 50, "length2": 15, "length3": 19, "length44": 100, "length5": 150,
                  "length6": 171, "length66": 172}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    keys = ("length", "length2", "length3", "length4", "length44", "length5", "length6", "length66")
    e = [c.ewm(span=int(p[k]), adjust=False).mean() for k in keys]
    up_l = c > e[0]
    dn_l = c < e[0]
    for a, b in zip(e[:-1], e[1:]):
        up_l &= a > b
        dn_l &= a < b
    hs, ls = [h.shift(k) for k in range(7)], [lo.shift(k) for k in range(7)]
    long_ = (up_l & (c > hs[1]) & (hs[1] > hs[2]) & (c > hs[3]) & (c > hs[4]) & (c > hs[5]) & (hs[5] > hs[6])).to_numpy()
    short_ = (dn_l & (c < ls[1]) & (ls[1] < ls[2]) & (c < ls[3]) & (c < ls[4]) & (c < ls[5]) & (ls[5] < ls[6])).to_numpy()
    xl = (e[0] < e[1]) & (e[1] < e[2]) & (e[2] < e[3])
    xs = (e[0] > e[1]) & (e[1] > e[2]) & (e[2] > e[3])
    cu = pd.Series(True, index=c.index)
    co = pd.Series(True, index=c.index)
    for k in range(4):
        cu &= (lo < e[k]) & (lo.shift(1) >= e[k].shift(1))
        co &= (h > e[k]) & (h.shift(1) <= e[k].shift(1))
    xl, xs = (xl | cu).to_numpy(), (xs | co).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if long_[i] and pos != 1:
            new = 1
        elif short_[i] and pos != -1:
            new = -1
        if pos == 1 and xl[i] and new == 1:
            new = 0
        if pos == -1 and xs[i] and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
