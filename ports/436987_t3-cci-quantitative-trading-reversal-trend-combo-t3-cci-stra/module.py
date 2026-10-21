"""123 reversal and T3-smoothed CCI combination, 1-hour bars: the 123 reversal state (two closes against a stochastic 14 test) and the sign of a T3 (b 0.618) of the CCI 14 agreeing long go long, agreeing short go
short, disagreeing close all; reversing.
Port of FMZ strategy #436987 "量化交易反转趋势串并T3-CCI策略Quantitative-Trading-Reversal-Trend-Combo-T3-CCI-Strategy" (Combo Backtest 123 Reversal & FX Sniper: T3-CCI).

FMZ source id: 436987

Source
    https://www.fmz.com/strategy/436987 (PineScript v4, FMZ last modified 2023-12-29 10:44:31).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 153-214), 123: length 14, K smoothing 1, D 3, level 50; CCI 14, T3 period 5, b 0.618; reverse off
    Reversal123: pos = 1 if close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > 50, -1 on the mirror, else pos[1]
    T3_CCI: e1..e6 = w1 x input + w2 x nz(e[1]) chained on cci(close, 14), w1 = 2 / (nr + 1), nr = 1 + 0.5 (5 - 1);  xccir = c1 e6 + c2 e5 + c3 e4 + c4 e3;  pos = sign(xccir) else pos[1];  agree -> entry, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * cci = (close - sma(close, 14)) / (0.015 x mean absolute deviation). The six smoothing stages carry
      nz() of their own earlier values as written (a stage that met na restarts from 0). The 123 test is
      read as written. The state is a level, so the entry is sent on every bar of the state; state 0
      closes. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and CCI sign.
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

NAME = "fmz_436987_reversal123_t3_cci_combo"
FAMILY = "reversal_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "cci_period": [14, 20],
}
DEFAULT_PARAMS = {"length": 14, "cci_period": 14, "k_smoothing": 1, "d_length": 3, "level": 50.0,
                  "t3_period": 5, "b": 0.618, "reverse": False}


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


def _t3_cci(c, n_cci, t3, b):
    sma = c.rolling(n_cci).mean()
    mad = c.rolling(n_cci).apply(lambda v: np.abs(v - v.mean()).mean(), raw=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        cci = ((c - sma) / (0.015 * mad)).to_numpy()
    b2, b3 = b * b, b * b * b
    k1, k2, k3, k4 = -b3, 3 * (b2 + b3), -3 * (2 * b2 + b + b3), 1 + 3 * b + b3 + 3 * b2
    nn = 1 if t3 < 1 else t3
    nr = 1 + 0.5 * (nn - 1)
    w1 = 2 / (nr + 1)
    w2 = 1 - w1
    m = len(cci)
    e = np.zeros((6, m))
    out = np.full(m, np.nan)
    prev = [np.nan] * 6
    for i in range(m):
        x = cci[i]
        for k in range(6):
            pk = 0.0 if np.isnan(prev[k]) else prev[k]
            x = w1 * x + w2 * pk
            e[k, i] = x
        prev = [e[k, i] for k in range(6)]
        out[i] = k1 * e[5, i] + k2 * e[4, i] + k3 * e[3, i] + k4 * e[2, i]
    return out


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
    xr = _t3_cci(c, int(p["cci_period"]), int(p["t3_period"]), float(p["b"]))
    m = len(c)
    sig = np.zeros(m)
    p123 = pt = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if up_[i]:
                p123 = 1.0
            elif dn_[i]:
                p123 = -1.0
            if xr[i] > 0:
                pt = 1.0
            elif xr[i] < 0:
                pt = -1.0
            sig[i] = 1.0 if (p123 == 1.0 and pt == 1.0) else (-1.0 if (p123 == -1.0 and pt == -1.0) else 0.0)
    if p["reverse"]:
        sig = -sig
    ix = bars_df.index
    flat = pd.Series(sig == 0, index=ix)
    return pd.Series(sig == 1, index=ix), flat, pd.Series(sig == -1, index=ix), flat.copy()


def portfolio_kwargs(**params):
    return {}
