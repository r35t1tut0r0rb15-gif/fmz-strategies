"""123 reversal and CMOav combination, 3-hour bars: the 123 reversal state (two closes against a stochastic 14 test) and the average of three CMOs (5 / 10 / 20; above 70: long, under -70: short) agreeing long
go long, agreeing short go short, disagreeing close all; reversing.
Port of FMZ strategy #438473 "Momentum Reversal Combo Strategy" (Combo).

FMZ source id: 438473

Source
    https://www.fmz.com/strategy/438473 (PineScript v4, FMZ last modified 2024-01-12 12:22:47).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 224-270), 123: length 14, K smoothing 1, D 3, level 50; CMO 5 / 10 / 20, bands 70 / -70; reverse off
    CMOav: nRes = 100 x (sum(mom, 5) / sum(|mom|, 5) + the same over 10 and 20) / 3;  pos = 1 if nRes > 70, -1 if nRes < -70, else pos[1]
    Reversal123 as in the combo family;  agree -> entry, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 123 test is read as written. The states are levels, so the entry is sent on every bar of the
      agreement; disagreement closes. REVERSAL INTENDED. No sizing code. FREQ = "3h" from the backtest
      header (bars on UTC multiples of 3 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and CMO bands.
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

NAME = "fmz_438473_reversal123_cmoav_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "top_band": [70, 50],
}
DEFAULT_PARAMS = {"length": 14, "top_band": 70.0, "k_smoothing": 1, "d_length": 3, "level": 50.0,
                  "length1": 5, "length2": 10, "length3": 20, "reverse": False}


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
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    vfast = st.rolling(int(p["k_smoothing"])).mean()
    vslow = vfast.rolling(int(p["d_length"])).mean()
    lvl = float(p["level"])
    c1, c2 = c.shift(1), c.shift(2)
    up_ = ((c2 < c1) & (c > c1) & (vfast < vslow) & (vfast > lvl)).to_numpy()
    dn_ = ((c2 > c1) & (c < c1) & (vfast > vslow) & (vfast < lvl)).to_numpy()
    mom = c.diff()
    res = 0.0
    with np.errstate(divide="ignore", invalid="ignore"):
        for k in (int(p["length1"]), int(p["length2"]), int(p["length3"])):
            res = res + mom.rolling(k).sum() / mom.abs().rolling(k).sum()
    res = (100.0 * res / 3).to_numpy()
    top = float(p["top_band"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    p123 = pcm = 0
    for i in range(m):
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        if res[i] > top:
            pcm = 1
        elif res[i] < -top:
            pcm = -1
        tgt[i] = 1 if (p123 == 1 and pcm == 1) else (-1 if (p123 == -1 and pcm == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
