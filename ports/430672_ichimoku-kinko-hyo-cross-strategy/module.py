"""Ichimoku basic, 1-hour bars: Tenkan over Kijun, a positive 25-bar momentum and the close above the cloud plotted 25 bars
ago goes long; the mirror goes short.
Port of FMZ strategy #430672 "Ichimoku Kinko Hyo Cross Strategy" (Ichimoku Kinko Hyo: Basic Strategy).

FMZ source id: 430672

Source
    https://www.fmz.com/strategy/430672 (PineScript v4, FMZ last modified 2023-10-31 15:00:43).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 203-249), Tenkan 9, Kijun 26, Senkou B 52, offsets 26
    bullish = tenkan > kijun and mom(close, 25) > 0 and close > max(senkouA[25], senkouB[25]) -> entry long
    bearish = tenkan < kijun and mom(close, 25) < 0 and close < min(senkouA[25], senkouB[25]) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both entry switches are on, so the strategy.close lines (only when one side is switched off)
      never act. The cloud is read 25 bars back (completed values).
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel midpoints and momentum signs.
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

NAME = "fmz_430672_ichimoku_basic_cloud"
FAMILY = "ichimoku"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ts_bars": [9, 20],
    "ks_bars": [26, 60],
}
DEFAULT_PARAMS = {"ts_bars": 9, "ks_bars": 26, "ssb_bars": 52, "cs_offset": 26, "ss_offset": 26}


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
    mid = lambda n: (lo.rolling(n).min() + h.rolling(n).max()) / 2  # noqa: E731
    tenkan, kijun = mid(int(p["ts_bars"])), mid(int(p["ks_bars"]))
    sa, sb = (tenkan + kijun) / 2, mid(int(p["ssb_bars"]))
    k = int(p["ss_offset"]) - 1
    ss_high = np.maximum(sa.shift(k), sb.shift(k))
    ss_low = np.minimum(sa.shift(k), sb.shift(k))
    mom = c - c.shift(int(p["cs_offset"]) - 1)
    bull = ((tenkan > kijun) & (mom > 0) & (c > ss_high)).to_numpy()
    bear = ((tenkan < kijun) & (mom < 0) & (c < ss_low)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if bull[i]:
            pos = 1
        elif bear[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
