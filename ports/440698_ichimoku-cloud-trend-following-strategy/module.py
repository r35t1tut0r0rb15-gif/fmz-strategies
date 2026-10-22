"""Ichimoku pull-backs and cloud breakouts, 2-hour bars: above the displaced cloud with the close above the high 26 bars back, a Kijun pull-back or a cloud breakout goes long; below the cloud, a Kijun
pull-back (or, as written, the long breakout test) goes short; the close crossing the Kijun closes; reversing.
Port of FMZ strategy #440698 "Ichimoku Cloud Trend Following Strategy" (Ichimoku trendfollowing).

FMZ source id: 440698

Source
    https://www.fmz.com/strategy/440698 (PineScript v3, FMZ last modified 2024-02-01 11:34:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 149-240), Tenkan 9, Kijun 26, Senkou B 52, displacement 26; window from 2010 (window() is true)
    filtroLong = close > max(spanA[26], spanB[26]) and high[26] < close;  long = (kijun < tenkan and low < kijun and close > kijun or breakout long) and filtroLong -> entry Long
    filtroShort = close < min(spanA[26], spanB[26]) and low[26] > close;  short = (kijun > tenkan and high > kijun and close < kijun or breakout LONG) and filtroShort -> entry Short;  close < kijun -> close Long, close > kijun -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cloud is read 26 bars back and the Chikou test compares with the high / low 26 bars back, so
      only past bars are used. The short side tests the long breakout as written (it cannot hold below
      the cloud, so shorts come from the pull-back test). A close acts only on the held position; one
      after a reversing entry leaves the reversal standing (as #438020). strategy.entry reverses:
      REVERSAL INTENDED. The capital, per-order commission and slippage are sizing and costs. FREQ =
      "2h" from the backtest header (bars on UTC multiples of 2 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders; displaced values from past bars.
    2 generic: PASS, Ichimoku lines and cloud.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: capital, commission and slippage settings.
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

NAME = "fmz_440698_ichimoku_pullback_breakout"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tenkan": [9, 20],
    "kijun": [26, 60],
}
DEFAULT_PARAMS = {"tenkan": 9, "kijun": 26, "span_b": 52, "disp": 26}


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

    def mid(n):
        return (lo.rolling(n).min() + h.rolling(n).max()) / 2

    tk, kj = mid(int(p["tenkan"])), mid(int(p["kijun"]))
    sa, sb = (tk + kj) / 2, mid(int(p["span_b"]))
    d = int(p["disp"])
    top = np.maximum(sa.shift(d), sb.shift(d))
    bot = np.minimum(sa.shift(d), sb.shift(d))
    f_l = (c > top) & (h.shift(d) < c)
    f_s = (c < bot) & (lo.shift(d) > c)
    pb_l = (kj < tk) & (lo < kj) & (c > kj)
    pb_s = (kj > tk) & (h > kj) & (c < kj)
    bo_l = (c > top) & (c.shift(1) <= top.shift(1)) & (c > tk) & (c > kj)
    L = ((pb_l | bo_l) & f_l).to_numpy()
    S = ((pb_s | bo_l) & f_s).to_numpy()
    XL, XS = (c < kj).to_numpy(), (c > kj).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if L[i]:
            new = 1
        if S[i]:
            new = -1
        if XL[i] and pos == 1 and new == 1:
            new = 0
        if XS[i] and pos == -1 and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
