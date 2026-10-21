"""123 reversal and Ehlers band-pass trend combination, 1-hour bars: the 123 reversal state (two closes against a stochastic 14 test) and the sign of the 40-bar mean of a 20-bar band-pass filter of hl2 agreeing
long go long, agreeing short go short, disagreeing close all; reversing.
Port of FMZ strategy #436791 "Dual factor Reversal Trading Strategy" (Combo Backtest 123 Reversal & Extracting The Trend).

FMZ source id: 436791

Source
    https://www.fmz.com/strategy/436791 (PineScript v4, FMZ last modified 2023-12-27 17:22:31).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 191-234), 123: length 14, K smoothing 1, D 3, level 50; ETT: length 20, delta 0.5, trigger 0; reverse off
    Reversal123: pos = 1 if close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > 50, -1 on the mirror, else pos[1]
    ETT: bp = 0.5 (1 - alpha)(hl2 - hl2[2]) + beta (1 + alpha) nz(bp[1]) - alpha nz(bp[2]);  xMean = sma(bp, 40);  pos = 1 if xMean > 0, -1 if < 0, else pos[1];  both agree -> entry, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * beta, gamma and alpha use the script's 3.1415 for pi, as written. The band-pass has no value until
      hl2[2] exists and then carries nz() of its own earlier values. The 123 test is read as written (a
      long needs the fast stochastic UNDER its slow line and above 50). The state is a level, so the entry
      is sent on every bar of the state; state 0 closes. REVERSAL INTENDED. No sizing code. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and band-pass sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND435522 (2 members, best partner #435522, Jaccard 0.653); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436791_reversal123_bandpass_trend_combo"
FAMILY = "reversal_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "length_ett": [20, 40],
}
DEFAULT_PARAMS = {"length": 14, "length_ett": 20, "k_smoothing": 1, "d_length": 3, "level": 50.0, "delta": 0.5,
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


def _bandpass_mean(bars_df, n, delta):
    pr = ((bars_df["high"] + bars_df["low"]) / 2).to_numpy(dtype=float)
    beta = np.cos(3.1415 * (360.0 / n) / 180.0)
    gamma = 1.0 / np.cos(3.1415 * (720.0 * delta / n) / 180.0)
    alpha = gamma - np.sqrt(gamma * gamma - 1.0)
    m = len(pr)
    bp = np.full(m, np.nan)
    for i in range(2, m):
        b1 = 0.0 if np.isnan(bp[i - 1]) else bp[i - 1]
        b2 = 0.0 if np.isnan(bp[i - 2]) else bp[i - 2]
        bp[i] = 0.5 * (1 - alpha) * (pr[i] - pr[i - 2]) + beta * (1 + alpha) * b1 - alpha * b2
    return pd.Series(bp, index=bars_df.index).rolling(2 * n).mean().to_numpy()


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
    xm = _bandpass_mean(bars_df, int(p["length_ett"]), float(p["delta"]))
    trig = float(p["trigger"])
    m = len(c)
    sig = np.zeros(m)
    p123 = pet = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if up_[i]:
                p123 = 1.0
            elif dn_[i]:
                p123 = -1.0
            if xm[i] > trig:
                pet = 1.0
            elif xm[i] < trig:
                pet = -1.0
            sig[i] = 1.0 if (p123 == 1.0 and pet == 1.0) else (-1.0 if (p123 == -1.0 and pet == -1.0) else 0.0)
    if p["reverse"]:
        sig = -sig
    ix = bars_df.index
    flat = pd.Series(sig == 0, index=ix)
    return pd.Series(sig == 1, index=ix), flat, pd.Series(sig == -1, index=ix), flat.copy()


def portfolio_kwargs(**params):
    return {}
