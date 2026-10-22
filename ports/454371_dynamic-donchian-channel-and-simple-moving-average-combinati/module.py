"""Donchian 20 (offset 1) touches on the side of the SMA 200, 4-hour bars: a low at or under the previous 20-bar low with the close over the SMA 200 goes long, a high at or over the previous 20-bar high with the close under it goes short; touching the opposite band closes; reversing.
Port of FMZ strategy #454371 "Dynamic Donchian Channel and Simple Moving Average Combination Quantitative Strategy" (FBK Donchian Channel Strategy).

FMZ source id: 454371

Source
    https://www.fmz.com/strategy/454371 (PineScript v5, FMZ last modified 2024-06-17 17:29:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-141), Donchian 20, offset 1; SMA 200; trade type Both; the test window helper returns true
    low <= lower[1] and close > sma -> entry Long;  high >= upper[1] -> close Long;  high >= upper[1] and close < sma -> entry Short;  low <= lower[1] -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The calls run in source order: an entry on the held side is ignored, an opposite entry
      reverses, and a close acts only on the trade held into the bar when no earlier call reversed it;
      a long entry and the long's close on one bar leave a flat position flat (the close finds no
      trade) and close a held long. The test window helper returns true. REVERSAL INTENDED. No sizing
      code. FREQ = "4h" from the backtest header (UTC-aligned 4-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Donchian touches with an SMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the test window is always on).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_454371_donchian20_touch_sma200_side_reversal"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [20, 50],
    "sma_len": [200, 100],
}
DEFAULT_PARAMS = {"period": 20, "sma_len": 200, "offset": 1}


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
    n, k = int(p["period"]), int(p["offset"])
    upper = h.rolling(n).max().shift(k)
    lower = lo.rolling(n).min().shift(k)
    sma = c.rolling(int(p["sma_len"])).mean()
    el = ((lo <= lower) & (c > sma)).to_numpy()
    xl = (h >= upper).to_numpy()
    es = ((h >= upper) & (c < sma)).to_numpy()
    xs = (lo <= lower).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        cur = pos
        if el[i] and cur != 1:
            cur = 1
        if xl[i] and pos == 1 and cur == 1:
            cur = 0
        if es[i] and cur != -1:
            cur = -1
        if xs[i] and pos == -1 and cur == -1:
            cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
