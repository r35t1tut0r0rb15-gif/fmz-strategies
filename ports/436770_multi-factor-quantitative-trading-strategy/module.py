"""123 reversal and psychological line combination, 1-hour bars: the 123 reversal state (two closes against a stochastic 14 test) and the psychological line state (share of up closes over 20 bars above or
under 50 %) agreeing long go long, agreeing short go short, disagreeing close all; reversing.
Port of FMZ strategy #436770 "Multi factor Quantitative Trading Strategy" (Combo Backtest 123 Reversal & Psychological line).

FMZ source id: 436770

Source
    https://www.fmz.com/strategy/436770 (PineScript v4, FMZ last modified 2023-12-27 15:46:27).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 136-174), 123: length 14, K smoothing 1, D 3, level 50; PSY length 20; reverse off
    Reversal123: pos = 1 if close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > 50, -1 on the mirror, else pos[1];  PLine: xPSY = sum(close > close[1], 20) / 20 x 100, pos = 1 above 50, -1 below, else pos[1]
    pos = 1 when both are 1, -1 when both are -1, else 0;  possig 1 -> entry Long, -1 -> entry Short, 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 123 test is read as written (a long needs the fast stochastic UNDER its slow line and above 50).
      The first PSY change has no earlier close and counts as no up close. The state is a level, so the
      entry is sent on every bar of the state; a same-side entry while in the position is ignored
      (pyramiding 0); state 0 closes. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns and dimensionless oscillators.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #440094, Jaccard 0.712); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436770_reversal123_psy_line_combo"
FAMILY = "reversal_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "length_pline": [20, 12],
}
DEFAULT_PARAMS = {"length": 14, "length_pline": 20, "k_smoothing": 1, "d_length": 3, "level": 50.0,
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
    npl = int(p["length_pline"])
    psy = ((c > c1).astype(float).rolling(npl).sum() / npl * 100.0).to_numpy()
    m = len(c)
    sig = np.zeros(m)
    p123 = ppl = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if up_[i]:
                p123 = 1.0
            elif dn_[i]:
                p123 = -1.0
            if psy[i] > 50:
                ppl = 1.0
            elif psy[i] < 50:
                ppl = -1.0
            sig[i] = 1.0 if (p123 == 1.0 and ppl == 1.0) else (-1.0 if (p123 == -1.0 and ppl == -1.0) else 0.0)
    if p["reverse"]:
        sig = -sig
    ix = bars_df.index
    flat = pd.Series(sig == 0, index=ix)
    return pd.Series(sig == 1, index=ix), flat, pd.Series(sig == -1, index=ix), flat.copy()


def portfolio_kwargs(**params):
    return {}
