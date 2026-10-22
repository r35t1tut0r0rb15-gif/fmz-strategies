"""Zero-lag TEMA crossings of a Heikin-Ashi-style close against hlc3, 1-hour bars: the hlc3 zero-lag TEMA (55) crossing over the HA-close one goes long, crossing under goes short; reversing.
Port of FMZ strategy #442256 "Adaptive Moving Average Crossover System with Momentum Breakout" (YASIN Crossover Strategy).

FMZ source id: 442256

Source
    https://www.fmz.com/strategy/442256 (PineScript v5, FMZ last modified 2024-02-20 15:43:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 117-155), EMA length 55; source ohlc4; session t1 unused
    haOpen = na(haOpen[1]) ? ohlc4 : (ohlc4 + haOpen[1]) / 2;  haC = (ohlc4 + haOpen + high + low) / 4;  TMA1 = TEMA(haC, 55), TMA2 = TEMA(TMA1, 55), YASIN = 2 TMA1 - TMA2;  YASIN1 the same from hlc3
    crossover(YASIN1, YASIN) -> entry Buy;  crossunder -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The haOpen recursion averages ohlc4 with its own previous value, as written. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, zero-lag TEMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442256_yasin_zero_lag_tema_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [55, 30],
}
DEFAULT_PARAMS = {"ema_length": 55}


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


def _tema(x, n):
    e1 = x.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    e3 = e2.ewm(span=n, adjust=False).mean()
    return 3 * e1 - 3 * e2 + e3


def _zl(x, n):
    t1 = _tema(x, n)
    t2 = _tema(t1, n)
    return t1 + (t1 - t2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    src = ((o + h + lo + c) / 4).to_numpy(dtype=float)
    m = len(src)
    hao = np.empty(m)
    for i in range(m):
        hao[i] = src[i] if i == 0 else (src[i] + hao[i - 1]) / 2
    hac = (pd.Series(src, index=c.index) + pd.Series(hao, index=c.index) + h + lo) / 4
    n = int(p["ema_length"])
    y = _zl(hac, n)
    y1 = _zl((h + lo + c) / 3, n)
    up = (y1 > y) & (y1.shift(1) <= y.shift(1))
    dn = (y1 < y) & (y1.shift(1) >= y.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
