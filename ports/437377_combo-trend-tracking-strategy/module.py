"""123 reversal and Blau's directional trend index combination, 15-minute bars: the 123 reversal state (two closes against a stochastic 14 test) and the contrarian DTI state (above 45 short, under -45 long)
agreeing long go long, agreeing short go short, disagreeing close all; reversing.
Port of FMZ strategy #437377 "Combo Trend Tracking Strategy" (Combo Backtest 123 Reversal & Directional Trend Index (DTI)).

FMZ source id: 437377

Source
    https://www.fmz.com/strategy/437377 (PineScript v4, FMZ last modified 2024-01-02 10:41:30).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 206-252), 123: length 14, K smoothing 1, D 3, level 50; DTI r 14, s 10, u 5, OS 45, OB -45; reverse off
    DTI = 100 ema3(HMU - LMD) / ema3(|HMU - LMD|) (triple EMA r / s / u; HMU = up move of the high, LMD = down move of the low);  pos = -1 if DTI > 45, 1 if DTI < -45, else pos[1]
    Reversal123 as in the combo family;  agree -> entry, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The first bar's moves count as 0 (na comparisons false). The 123 test is read as written. The state is
      a level, so the entry is sent on every bar of the state; state 0 closes. REVERSAL INTENDED. No sizing
      code. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and a dimensionless trend index.
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

NAME = "fmz_437377_reversal123_dti_combo"
FAMILY = "reversal_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "r": [14, 25],
}
DEFAULT_PARAMS = {"length": 14, "r": 14, "k_smoothing": 1, "d_length": 3, "level": 50.0, "s": 10, "u": 5,
                  "os": 45.0, "ob": -45.0, "reverse": False}


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
    dh, dl = h.diff(), lo.diff()
    hmu = dh.where(dh > 0, 0.0)
    lmd = (-dl).where(dl < 0, 0.0)
    xp = hmu - lmd

    def ema3(x):
        for k in ("r", "s", "u"):
            x = x.ewm(span=int(p[k]), adjust=False).mean()
        return x

    a, b = ema3(xp), ema3(xp.abs())
    with np.errstate(divide="ignore", invalid="ignore"):
        dti = (100 * a / b).where(b != 0, 0.0).to_numpy()
    os_, ob = float(p["os"]), float(p["ob"])
    m = len(c)
    sig = np.zeros(m)
    p123 = pd_ = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if up_[i]:
                p123 = 1.0
            elif dn_[i]:
                p123 = -1.0
            if dti[i] > os_:
                pd_ = -1.0
            elif dti[i] < ob:
                pd_ = 1.0
            sig[i] = 1.0 if (p123 == 1.0 and pd_ == 1.0) else (-1.0 if (p123 == -1.0 and pd_ == -1.0) else 0.0)
    if p["reverse"]:
        sig = -sig
    ix = bars_df.index
    flat = pd.Series(sig == 0, index=ix)
    return pd.Series(sig == 1, index=ix), flat, pd.Series(sig == -1, index=ix), flat.copy()


def portfolio_kwargs(**params):
    return {}
