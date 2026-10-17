"""HPotter combo of the 123 reversal and a KST-style rate-of-change sum, 1-hour bars: long while both sides say up, short
while both say down, flat otherwise. The KST side is the sign of SMA10(ROC 6) + 2 SMA10(ROC 10) + 3 SMA9(ROC 15) + 4
SMA15(ROC 20).
Port of FMZ strategy #432883 "123 Reversal Moving Average Convergence Divergence Combination Strategy" (Combo Backtest 123 Reversal & MovROC (KST indicator)).

FMZ source id: 432883

Source
    https://www.fmz.com/strategy/432883 (PineScript v4, FMZ last modified 2023-11-22 14:49:41).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 171-210), stoch 14 / 1 / 3, level 50; ROC 6 / 10 / 15 / 20 with SMAs 10 / 10 / 9 / 15
    kst = sma(roc(c, 6), 10) + 2 sma(roc(c, 10), 10) + 3 sma(roc(c, 15), 9) + 4 sma(roc(c, 20), 15)
    pkst = kst > 0 ? 1 : kst < 0 ? -1 : pkst[1];  p123 as Reversal123(14, 1, 3, 50)
    both 1 -> entry long;  both -1 -> entry short;  otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * roc(x, n) = 100 x (x - x[n]) / x[n]. Each side keeps its last state until it changes.
      strategy.entry reverses: REVERSAL INTENDED. reverse is false. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and rate-of-change sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #432231, Jaccard 0.671); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432883_combo_123_kst"
FAMILY = "combo_123_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "level": [50, 40],
}
DEFAULT_PARAMS = {"length": 14, "k_smooth": 1, "d_len": 3, "level": 50}


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
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["k_smooth"])).mean()
    d = k.rolling(int(p["d_len"])).mean()
    lv = float(p["level"])
    c1, c2 = c.shift(1), c.shift(2)
    a_up = ((c2 < c1) & (c > c1) & (k < d) & (k > lv)).to_numpy()
    a_dn = ((c2 > c1) & (c < c1) & (k > d) & (k < lv)).to_numpy()
    roc = lambda m_: 100 * (c - c.shift(m_)) / c.shift(m_)  # noqa: E731
    kst = (roc(6).rolling(10).mean() + 2 * roc(10).rolling(10).mean() + 3 * roc(15).rolling(9).mean()
           + 4 * roc(20).rolling(15).mean()).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    s1 = s2 = 0
    for i in range(m):
        if a_up[i]:
            s1 = 1
        elif a_dn[i]:
            s1 = -1
        if kst[i] > 0:
            s2 = 1
        elif kst[i] < 0:
            s2 = -1
        tgt[i] = 1 if (s1 == 1 and s2 == 1) else (-1 if (s1 == -1 and s2 == -1) else 0)
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
