"""123 reversal state with an empirical-mode band-pass state, 1-hour bars: both long opens a long, both short opens a short, any other
combination closes (the "Trade reverse" input flips the side).
Port of FMZ strategy #435522 "Dual Reversion Balance Strategy" (Combo Backtest 123 Reversal & Empirical Mode Decomposition).

FMZ source id: 435522

Source
    https://www.fmz.com/strategy/435522 (PineScript v4, FMZ last modified 2023-12-15 16:56:20).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 163-213), stoch 14 (K smoothing 1, D 3, level 50); band-pass period 20, delta 0.5, fraction 0.1
    123: close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > 50 -> 1;  the mirror -> -1;  else the last state
    EMD: bp = 0.5 (1 - alpha) (hl2 - hl2[2]) + beta (1 + alpha) bp[1] - alpha bp[2];  xMean = sma(bp, 40);  xPeak / xValley = bp[1] at local peaks / valleys; nAvrPeak = 0.1 sma(xPeak, 50);  pos = xMean over both levels ? 1 : under both ? -1 : last
    pos = both 1 -> 1;  both -1 -> -1;  else 0;  possig = reverse ? -pos : pos;  entry long / short;  possig == 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * beta = cos(3.1415 x (360 / Length) / 180), gamma = 1 / cos(3.1415 x (720 Delta / Length) / 180),
      alpha = gamma - sqrt(gamma^2 - 1), with the author's pi of 3.1415. The recursive filter starts from
      zero (nz). Two persistent states combined; a flip from one agreed side to the other on one bar
      is a reversal (REVERSAL INTENDED); any disagreement closes. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, pattern state and a band-pass filter state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND435522 (2 members, best partner #436791, Jaccard 0.653); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import math

import numpy as np
import pandas as pd

NAME = "fmz_435522_reversal_123_empirical_mode"
FAMILY = "reversal_pattern"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reverse": [False, True],
    "length_emd": [20, 30],
}
DEFAULT_PARAMS = {"reverse": False, "length_emd": 20, "delta": 0.5, "fraction": 0.1, "length": 14, "k_smooth": 1,
                  "d_len": 3, "level": 50}


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


def _state(up, dn):
    out = np.zeros(len(up), dtype=np.int8)
    q = 0
    for i in range(len(up)):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        out[i] = q
    return out


def _empirical(hl2, length, delta, fraction):
    beta = math.cos(3.1415 * (360 / length) / 180)
    gamma = 1 / math.cos(3.1415 * (720 * delta / length) / 180)
    alpha = gamma - math.sqrt(gamma * gamma - 1)
    x = hl2.to_numpy(dtype=float)
    m = len(x)
    bp = np.zeros(m)
    for i in range(m):
        b1 = bp[i - 1] if i >= 1 else 0.0
        b2 = bp[i - 2] if i >= 2 else 0.0
        x2 = x[i - 2] if i >= 2 else np.nan
        bp[i] = 0.5 * (1 - alpha) * (x[i] - x2) + beta * (1 + alpha) * b1 - alpha * b2
    s = pd.Series(bp, index=hl2.index)
    mean = s.rolling(2 * length).mean()
    peak, valley = np.zeros(m), np.zeros(m)
    for i in range(m):
        pp = peak[i - 1] if i >= 1 else 0.0
        vv = valley[i - 1] if i >= 1 else 0.0
        if i >= 2 and bp[i - 1] > bp[i] and bp[i - 1] > bp[i - 2]:
            pp = bp[i - 1]
        if i >= 2 and bp[i - 1] < bp[i] and bp[i - 1] < bp[i - 2]:
            vv = bp[i - 1]
        peak[i], valley[i] = pp, vv
    avr_peak = pd.Series(peak, index=hl2.index).rolling(50).mean() * fraction
    avr_valley = pd.Series(valley, index=hl2.index).rolling(50).mean() * fraction
    up = ((mean > avr_peak) & (mean > avr_valley)).to_numpy()
    dn = ((mean < avr_peak) & (mean < avr_valley)).to_numpy()
    return _state(up, dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    with np.errstate(invalid="ignore", divide="ignore"):
        raw = 100 * (c - lo.rolling(n).min()) / (h.rolling(n).max() - lo.rolling(n).min())
    vf = raw.rolling(int(p["k_smooth"])).mean()
    vs = vf.rolling(int(p["d_len"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    lv = float(p["level"])
    a = _state(((c2 < c1) & (c > c1) & (vf < vs) & (vf > lv)).to_numpy(),
               ((c2 > c1) & (c < c1) & (vf > vs) & (vf < lv)).to_numpy())
    b = _empirical((h + lo) / 2, int(p["length_emd"]), float(p["delta"]), float(p["fraction"]))
    pos = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0)).astype(np.int8)
    if p["reverse"]:
        pos = -pos
    prev = np.concatenate(([0], pos[:-1]))
    ix = bars_df.index
    return (pd.Series((pos == 1) & (prev != 1), index=ix), pd.Series((pos == 0) & (prev == 1), index=ix),
            pd.Series((pos == -1) & (prev != -1), index=ix), pd.Series((pos == 0) & (prev == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
