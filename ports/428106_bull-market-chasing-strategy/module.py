"""EMA 10 / 60 cross, 45-minute bars: EMA 10 crossing above EMA 60 goes long, crossing below goes short
(the short switch is on by default).
Port of FMZ strategy #428106 "Bull Market Chasing Strategy" (STB - Gianno Nano Strategy).

FMZ source id: 428106

Source
    https://www.fmz.com/strategy/428106 (PineScript v5, FMZ last modified 2023-09-28 16:23:41).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 156-190), EMA 10 / 60, shorts on
    crossover(ema10, ema60) -> entry long; crossunder -> entry short (shorts off: close the long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() line is commented out: Pine defaults (one position). Shorts on (default).
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented strategy() cash quantity stored in original_sizing.txt.
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

NAME = "fmz_428106_ema_10_60_cross"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_fast": [10, 20],
    "ema_slow": [60, 120],
}
DEFAULT_PARAMS = {"ema_fast": 10, "ema_slow": 60}


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
    a = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    b = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    up = ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    dn = ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()
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
