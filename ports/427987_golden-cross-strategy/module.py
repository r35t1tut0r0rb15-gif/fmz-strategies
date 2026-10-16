"""Golden cross, long only, 2-hour bars: SMA 50 crossing above SMA 200 goes long; crossing below closes.
Port of FMZ strategy #427987 "Golden Cross Strategy" ("Dumb strategy 2 - Golden Cross").

FMZ source id: 427987

Source
    https://www.fmz.com/strategy/427987 (PineScript v3, FMZ last modified 2023-09-27 16:23:51).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 154-198), SMA 50 / 200
    crossover(sma50, sma200) -> entry long; crossunder -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * testPeriod() is true (the date inputs only colour the background).
    * Long only. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427987_golden_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "l_short": [50, 20],
    "l_long": [200, 100],
}
DEFAULT_PARAMS = {"l_short": 50, "l_long": 200}


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
    f, s = c.rolling(int(p["l_short"])).mean(), c.rolling(int(p["l_long"])).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
