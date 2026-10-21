"""123 reversal and previous-high-over-EMA combination, 15-minute bars: the 123 reversal state (two closes against a stochastic 14 test) and the sign of the previous high minus the previous EMA 13 of the close
agreeing long go long, agreeing short go short, disagreeing close all; reversing.
Port of FMZ strategy #437515 "Dual Reversal High Low Strategy" (Combo Backtest 123 Reversal & High - EMA Strategy).

FMZ source id: 437515

Source
    https://www.fmz.com/strategy/437515 (PineScript v4, FMZ last modified 2024-01-03 13:56:04).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 126-163), 123: length 14, K smoothing 1, D 3, level 50; HEMA length 13; reverse off
    HEMA: nRes = high[1] - nz(ema(close, 13)[1]);  pos = 1 if nRes > 0, -1 if < 0, else pos[1]
    Reversal123 as in the combo family;  agree -> entry, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * nz() makes the EMA 0 on the first bar, as written. The 123 test is read as written. The state is a
      level, so the entry is sent on every bar of the state; state 0 closes. REVERSAL INTENDED. No sizing
      code. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and a high-over-EMA sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #432231, Jaccard 0.737); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437515_reversal123_high_ema_combo"
FAMILY = "reversal_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "length_hema": [13, 26],
}
DEFAULT_PARAMS = {"length": 14, "length_hema": 13, "k_smoothing": 1, "d_length": 3, "level": 50.0,
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
    ema1 = c.ewm(span=int(p["length_hema"]), adjust=False).mean().shift(1).fillna(0.0)
    nres = (h.shift(1) - ema1).to_numpy()
    m = len(c)
    sig = np.zeros(m)
    p123 = ph = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if up_[i]:
                p123 = 1.0
            elif dn_[i]:
                p123 = -1.0
            if nres[i] > 0:
                ph = 1.0
            elif nres[i] < 0:
                ph = -1.0
            sig[i] = 1.0 if (p123 == 1.0 and ph == 1.0) else (-1.0 if (p123 == -1.0 and ph == -1.0) else 0.0)
    if p["reverse"]:
        sig = -sig
    ix = bars_df.index
    flat = pd.Series(sig == 0, index=ix)
    return pd.Series(sig == 1, index=ix), flat, pd.Series(sig == -1, index=ix), flat.copy()


def portfolio_kwargs(**params):
    return {}
