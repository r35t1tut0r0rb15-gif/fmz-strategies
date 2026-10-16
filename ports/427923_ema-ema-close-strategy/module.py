"""EMA stack against EMA 55, 30-minute bars: EMAs 8, 13 and 21 and the close all above EMA 55 go long;
all below go short (between, the last side is kept).
Port of FMZ strategy #427923 "EMA Close Strategy" (EMA Candle Close Strategy).

FMZ source id: 427923

Source
    https://www.fmz.com/strategy/427923 (PineScript v4, FMZ last modified 2023-09-26 20:09:08).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 175-210), EMAs 8 / 13 / 21 / 55 / 200
    ema8, ema13, ema21 and close > ema55 -> entry long; all < ema55 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * EMA 200 is drawn only. Repeated same-side entries are ignored (pyramiding 0).
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
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

NAME = "fmz_427923_ema_stack_vs_ema55"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len4": [55, 100],
    "len3": [21, 34],
}
DEFAULT_PARAMS = {"len1": 8, "len2": 13, "len3": 21, "len4": 55}


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
    e = lambda n: c.ewm(span=int(n), adjust=False).mean()
    e1, e2, e3, e4 = e(p["len1"]), e(p["len2"]), e(p["len3"]), e(p["len4"])
    up = ((e1 > e4) & (e2 > e4) & (e3 > e4) & (c > e4)).to_numpy()
    dn = ((e1 < e4) & (e2 < e4) & (e3 < e4) & (c < e4)).to_numpy()
    m = len(up)
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
