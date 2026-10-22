"""123 reversal and Laguerre RSI combination, 5-minute bars: the 123 reversal state and the Laguerre RSI state (gamma 0.5; above 0.8: long, under 0.2: short) agreeing long go long, agreeing short go short,
disagreeing close all; reversing.
Port of FMZ strategy #439188 "Dual Factor Momentum Tracking Reversal Strategy" (Combo).

FMZ source id: 439188

Source
    https://www.fmz.com/strategy/439188 (PineScript v4, FMZ last modified 2024-01-18 11:33:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 150-196), 123: length 14, K smoothing 1, D 3, level 50; Laguerre gamma 0.5, bands 0.8 / 0.2; reverse off
    LB_RSI: L0..L3 Laguerre filter (nz seeds 1);  CU / CD sums;  RSI = CU / (CU + CD);  pos = 1 if > 0.8, -1 if < 0.2, else pos[1]
    Reversal123 as in the combo family;  agree -> entry, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Laguerre stages start from nz() = 1, as written. The 123 test is read as written. The states are
      levels; disagreement closes. REVERSAL INTENDED. No sizing code. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and a Laguerre RSI.
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

NAME = "fmz_439188_reversal123_laguerre_rsi_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "gamma": [0.5, 0.7],
}
DEFAULT_PARAMS = {"length": 14, "gamma": 0.5, "k_smoothing": 1, "d_length": 3, "level": 50.0,
                  "buy_band": 0.8, "sell_band": 0.2, "reverse": False}


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
    g = float(p["gamma"])
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    res = np.zeros(m)
    l0p = l1p = l2p = l3p = 1.0
    for i in range(m):
        l0 = (1 - g) * cv[i] + g * l0p
        l1 = -g * l0 + l0p + g * l1p
        l2 = -g * l1 + l1p + g * l2p
        l3 = -g * l2 + l2p + g * l3p
        cu = (l0 - l1 if l0 >= l1 else 0.0) + (l1 - l2 if l1 >= l2 else 0.0) + (l2 - l3 if l2 >= l3 else 0.0)
        cd = (0.0 if l0 >= l1 else l1 - l0) + (0.0 if l1 >= l2 else l2 - l1) + (0.0 if l2 >= l3 else l3 - l2)
        res[i] = cu / (cu + cd) if cu + cd != 0 else 0.0
        l0p, l1p, l2p, l3p = l0, l1, l2, l3
    bb, sb = float(p["buy_band"]), float(p["sell_band"])
    tgt = np.zeros(m, dtype=np.int8)
    p123 = plb = 0
    for i in range(m):
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        if res[i] > bb:
            plb = 1
        elif res[i] < sb:
            plb = -1
        tgt[i] = 1 if (p123 == 1 and plb == 1) else (-1 if (p123 == -1 and plb == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
