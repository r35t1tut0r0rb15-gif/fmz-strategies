"""123 reversal and DAPD band combination, 10-minute bars: the 123 reversal state (two closes against a stochastic 14 test) and the DAPD state (a high above the previous high plus the 21-bar average range: long;
a low under the previous low minus it: short) agreeing long go long, agreeing short go short, disagreeing close all; reversing.
Port of FMZ strategy #437769 "Reversal Momentum Compound Strategy" (Combo Backtest 123 Reversal & DAPD).

FMZ source id: 437769

Source
    https://www.fmz.com/strategy/437769 (PineScript v4, FMZ last modified 2024-01-05 14:06:21).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 157-195), 123: length 14, K smoothing 1, D 3, level 50; DAPD length 21; reverse off
    DAPD: nDAPD = sma(high, 21) - sma(low, 21);  pos = 1 if high > (high + nDAPD)[1], -1 if low < (low - nDAPD)[1], else pos[1]
    Reversal123 as in the combo family;  agree -> entry, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 123 test is read as written. The state is a level, so the entry is sent on every bar of the
      state; state 0 closes. REVERSAL INTENDED. No sizing code. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and an average-range band.
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

NAME = "fmz_437769_reversal123_dapd_combo"
FAMILY = "reversal_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "length_dapd": [21, 42],
}
DEFAULT_PARAMS = {"length": 14, "length_dapd": 21, "k_smoothing": 1, "d_length": 3, "level": 50.0,
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
    k = int(p["length_dapd"])
    dapd = h.rolling(k).mean() - lo.rolling(k).mean()
    top, bot = (h + dapd).shift(1), (lo - dapd).shift(1)
    tu, td = (h > top).to_numpy(), (lo < bot).to_numpy()
    m = len(c)
    sig = np.zeros(m)
    p123 = pd_ = 0.0
    for i in range(m):
        if up_[i]:
            p123 = 1.0
        elif dn_[i]:
            p123 = -1.0
        if tu[i]:
            pd_ = 1.0
        elif td[i]:
            pd_ = -1.0
        sig[i] = 1.0 if (p123 == 1.0 and pd_ == 1.0) else (-1.0 if (p123 == -1.0 and pd_ == -1.0) else 0.0)
    if p["reverse"]:
        sig = -sig
    ix = bars_df.index
    flat = pd.Series(sig == 0, index=ix)
    return pd.Series(sig == 1, index=ix), flat, pd.Series(sig == -1, index=ix), flat.copy()


def portfolio_kwargs(**params):
    return {}
