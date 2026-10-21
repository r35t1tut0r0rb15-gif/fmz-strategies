"""123 reversal and High Low Bands combination, 4-hour bars: the 123 reversal state (two closes against a stochastic 14 test) and the High Low Bands state (a close above the triangular SMA 14 + 1 %: long; under
it - 1 %: short) agreeing long go long, agreeing short go short, disagreeing close all; reversing.
Port of FMZ strategy #438457 "Dual Moving Average Strategy Combined with Stochastic Indicator" (Combo).

FMZ source id: 438457

Source
    https://www.fmz.com/strategy/438457 (PineScript v4, FMZ last modified 2024-01-12 11:16:52).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 160-198), 123: length 14, K smoothing 1, D 3, level 50; HLB length 14, shift 1 %; reverse off
    HLB: tma = sma(sma(close, 14), 14);  pos = 1 if close > tma x 1.01, -1 if close < tma x 0.99, else pos[1]
    Reversal123 as in the combo family;  agree -> entry, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 123 test is read as written. The states are levels, so the entry is sent on every bar of the
      agreement; disagreement closes. REVERSAL INTENDED. No sizing code. FREQ = "4h" from the backtest
      header (bars on UTC multiples of 4 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and percent bands of a triangular average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #429771, Jaccard 0.715); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438457_reversal123_high_low_bands_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "percent_shift": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 14, "percent_shift": 1.0, "k_smoothing": 1, "d_length": 3, "level": 50.0,
                  "length_hlb": 14, "reverse": False}


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
    k = int(p["length_hlb"])
    tma = c.rolling(k).mean().rolling(k).mean()
    sh = float(p["percent_shift"]) / 100
    hb_up = (c > tma * (1 + sh)).to_numpy()
    hb_dn = (c < tma * (1 - sh)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    p123 = phl = 0
    for i in range(m):
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        if hb_up[i]:
            phl = 1
        elif hb_dn[i]:
            phl = -1
        tgt[i] = 1 if (p123 == 1 and phl == 1) else (-1 if (p123 == -1 and phl == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
