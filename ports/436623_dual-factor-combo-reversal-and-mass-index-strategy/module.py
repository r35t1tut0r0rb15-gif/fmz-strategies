"""Combination of the 1-2-3 reversal and the Mass Index, 1-hour bars: both signals long goes long, both short goes short (reversing), anything else closes everything. The 1-2-3 reversal is a three-close turn with a fast / slow
stochastic cross above / below 50; the Mass Index sum over 26.5 reads short, under it long.
Port of FMZ strategy #436623 "Dual Factor Combo Reversal and Mass Index Strategy" (Combo Backtest 123 Reversal & MASS Index).

FMZ source id: 436623

Source
    https://www.fmz.com/strategy/436623 (PineScript v4, FMZ last modified 2023-12-26 12:20:57).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 154-196), 123 reversal 14 / 1 / 3 / 50; Mass Index 9 / 25 / 26.5; reverse off
    Reversal123: pos = 1 if close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > 50; -1 if the mirror (vFast > vSlow, vFast < 50); else pos[1]
    MASS: nRes = sum(ema(range, 9) / ema(ema(range, 9), 9), 25);  pos = -1 if nRes > 26.5, 1 if nRes < 26.5, else pos[1]
    pos = 1 if both 1, -1 if both -1, else 0;  possig 1 -> entry Long;  -1 -> entry Short;  0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both component positions keep their value between signals (the function series), so the combined
      position is a level. The entry is sent on every bar of the state; a same-side entry while in
      the position is ignored. REVERSAL INTENDED. The default quantity is sizing. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, reversal pattern and Mass Index states.
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

NAME = "fmz_436623_reversal123_mass_index_combo"
FAMILY = "combo_state"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 10],
    "trigger": [26.5, 25.0],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "length1": 9, "length2": 25,
                  "trigger": 26.5, "reverse": False}


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
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    vfast = st.rolling(int(p["k_smoothing"])).mean()
    vslow = vfast.rolling(int(p["d_length"])).mean()
    lvl = float(p["level"])
    c1, c2 = c.shift(1), c.shift(2)
    up_ = ((c2 < c1) & (c > c1) & (vfast < vslow) & (vfast > lvl)).to_numpy()
    dn_ = ((c2 > c1) & (c < c1) & (vfast > vslow) & (vfast < lvl)).to_numpy()
    e1 = (h - lo).ewm(span=int(p["length1"]), adjust=False).mean()
    e2 = e1.ewm(span=int(p["length1"]), adjust=False).mean()
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = (e1 / e2).where(e2 != 0, 0.0)
    nres = ratio.rolling(int(p["length2"])).sum().to_numpy()
    trig = float(p["trigger"])
    m = len(c)
    sig = np.zeros(m)
    p123 = pm = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if up_[i]:
                p123 = 1.0
            elif dn_[i]:
                p123 = -1.0
            if nres[i] > trig:
                pm = -1.0
            elif nres[i] < trig:
                pm = 1.0
            sig[i] = 1.0 if (p123 == 1.0 and pm == 1.0) else (-1.0 if (p123 == -1.0 and pm == -1.0) else 0.0)
    if p["reverse"]:
        sig = -sig
    ix = bars_df.index
    flat = pd.Series(sig == 0, index=ix)
    return pd.Series(sig == 1, index=ix), flat, pd.Series(sig == -1, index=ix), flat.copy()


def portfolio_kwargs(**params):
    return {}
