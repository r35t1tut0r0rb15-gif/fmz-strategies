"""123 reversal and Inertia combination, 1-hour bars: the 123 reversal state (two closes against a stochastic 14 test) and the Inertia state (EMA 14 of a 10-bar relative volatility index above 50: long;
under: short) agreeing long go long, agreeing short go short, disagreeing close all; reversing.
Port of FMZ strategy #438498 "Quantitative Dual Factor Reversal Inertia Trading Strategy" (Combo).

FMZ source id: 438498

Source
    https://www.fmz.com/strategy/438498 (PineScript v4, FMZ last modified 2024-01-12 14:38:02).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 177-221), 123: length 14, K smoothing 1, D 3, level 50; Inertia period 10, smooth 14; reverse off
    Inertia: sd = stdev(close, 10);  u = close > close[1] ? sd : 0, d = the other;  nU := (13 nU[1] + u) / 14, nD likewise;  RVI = 100 nU / (nU + nD);  pos = 1 if ema(RVI, 14) > 50, -1 if < 50, else pos[1]
    Reversal123 as in the combo family;  agree -> entry, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 123 test is read as written. The Inertia smoothing starts from nz() = 0; stdev is the population
      deviation. The states are levels, so the entry is sent on every bar of the agreement; disagreement
      closes. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and relative volatility.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426322 (2 members, best partner #426322, Jaccard 0.694); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438498_reversal123_inertia_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "period": [10, 20],
}
DEFAULT_PARAMS = {"length": 14, "period": 10, "k_smoothing": 1, "d_length": 3, "level": 50.0, "smooth": 14,
                  "reverse": False}


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
    sd = c.rolling(int(p["period"])).std(ddof=0).to_numpy()
    rising = (c > c1).to_numpy()
    m = len(c)
    rvi = np.full(m, np.nan)
    nu = nd = np.nan
    for i in range(m):
        u = sd[i] if rising[i] else 0.0
        d = 0.0 if rising[i] else sd[i]
        nu = (13 * (0.0 if np.isnan(nu) else nu) + u) / 14
        nd = (13 * (0.0 if np.isnan(nd) else nd) + d) / 14
        with np.errstate(divide="ignore", invalid="ignore"):
            rvi[i] = 100 * nu / (nu + nd)
    res = pd.Series(rvi, index=c.index).ewm(span=int(p["smooth"]), adjust=False).mean().to_numpy()
    tgt = np.zeros(m, dtype=np.int8)
    p123 = pin = 0
    for i in range(m):
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        if res[i] > 50:
            pin = 1
        elif res[i] < 50:
            pin = -1
        tgt[i] = 1 if (p123 == 1 and pin == 1) else (-1 if (p123 == -1 and pin == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
