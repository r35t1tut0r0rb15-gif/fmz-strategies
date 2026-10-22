"""HPotter combo of the 123 reversal and the Donchian Channel Width, 1-hour bars: long when the 123 state is long and the 20-bar channel width is under its 22-bar SMA, short when the 123 state is short and
the width above it, flat otherwise; reversing.
Port of FMZ strategy #442250 "Reversal Momentum Strategy with Double Confirmation" (Combo Backtest 123 Reversal & Donchian Channel Width).

FMZ source id: 442250

Source
    https://www.fmz.com/strategy/442250 (PineScript v4, FMZ last modified 2024-02-20 15:27:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 125-206), 123: stochastic 14, K smoothing 1, D 3, level 50; DCW length 20, smoothing 22; reverse off
    123: close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > 50 -> 1;  mirrored -> -1;  else previous
    DCW = highest(high, 20) - lowest(low, 20);  DCW > sma(DCW, 22) -> -1, < -> 1, else previous;  both 1 -> entry Long, both -1 -> entry Short, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both states are ported as written. The combined state is a level; disagreement closes. REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close pattern, stochastic and channel-width states.
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

NAME = "fmz_442250_reversal123_donchian_width_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "length_dcw": [20, 40],
}
DEFAULT_PARAMS = {"length": 14, "length_dcw": 20, "smooth_dcw": 22, "k_smoothing": 1, "d_length": 3,
                  "level": 50.0, "reverse": False}


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
    k = int(p["length_dcw"])
    w = h.rolling(k).max() - lo.rolling(k).min()
    ws = w.rolling(int(p["smooth_dcw"])).mean()
    w_dn, w_up = (w > ws).to_numpy(), (w < ws).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    p123 = pw = 0
    for i in range(m):
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        if w_dn[i]:
            pw = -1
        elif w_up[i]:
            pw = 1
        tgt[i] = 1 if (p123 == 1 and pw == 1) else (-1 if (p123 == -1 and pw == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
