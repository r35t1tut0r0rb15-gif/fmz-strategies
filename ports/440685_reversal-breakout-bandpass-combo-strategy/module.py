"""123 reversal and bandpass filter combo, 1-hour bars: long when the 123 state is up and the 20-bar bandpass of hl2 is above zero, short when the 123 state is down and the bandpass at or below zero, flat
when they disagree.
Port of FMZ strategy #440685 "Reversal Breakout Bandpass Combo Strategy" (Combo Backtest 123 Reversal & Bandpass Filter).

FMZ source id: 440685

Source
    https://www.fmz.com/strategy/440685 (PineScript v3, FMZ last modified 2024-02-01 10:45:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 131-173), 123: 14 / 1 / 3 / 50; bandpass length 20, delta 0.5, trigger 0; reverse off
    123 pos (close pattern and stochastic);  BP = 0.5 (1 - alpha)(hl2 - hl2[2]) + beta (1 + alpha) BP[1] - alpha BP[2];  pos = BP > 0 ? 1 : -1;  both 1 -> entry Long, both -1 -> entry Short, otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * beta = cos(3.14 x (360 / 20) / 180), gamma = 1 / cos(3.14 x (720 x 0.5 / 20) / 180), alpha =
      gamma - sqrt(gamma^2 - 1), with 3.14 as written; the filter starts from 0 (nz). The 123 test is
      read as written. The states are levels; disagreement closes. REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close pattern, stochastic and a bandpass filter.
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

NAME = "fmz_440685_reversal123_bandpass_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "length_bf": [20, 40],
}
DEFAULT_PARAMS = {"length": 14, "length_bf": 20, "k_smoothing": 1, "d_length": 3, "level": 50.0, "delta": 0.5,
                  "trigger": 0.0, "reverse": False}


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


def _bandpass(x, n, delta):
    beta = np.cos(3.14 * (360 / n) / 180)
    gamma = 1 / np.cos(3.14 * (720 * delta / n) / 180)
    alpha = gamma - np.sqrt(gamma * gamma - 1)
    xv = x.to_numpy(dtype=float)
    bp = np.full(len(xv), np.nan)
    b1 = b2 = 0.0
    for i in range(len(xv)):
        d = xv[i] - xv[i - 2] if i >= 2 else np.nan
        v = 0.5 * (1 - alpha) * d + beta * (1 + alpha) * b1 - alpha * b2
        bp[i] = v
        b2, b1 = b1, (0.0 if np.isnan(v) else v)
    return bp


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
    bp = _bandpass((h + lo) / 2, int(p["length_bf"]), float(p["delta"]))
    trig = float(p["trigger"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    p123 = pb = 0
    for i in range(m):
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        if bp[i] > trig:
            pb = 1
        elif bp[i] <= trig:
            pb = -1
        tgt[i] = 1 if (p123 == 1 and pb == 1) else (-1 if (p123 == -1 and pb == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
