"""123 reversal and centre-of-gravity channel combination, 3-hour bars: the 123 reversal state (stochastic 20, as the script passes it) and a close beyond the 14-bar regression line (offset 5) +- 1 % of the close
agreeing long go long, agreeing short go short, disagreeing close all; reversing.
Port of FMZ strategy #437553 "Reversal and Center of Gravity Integrated Trading Strategy Based on Multi strategy" (Combo Backtest 123 Reversal & Center Of Gravity).

FMZ source id: 437553

Source
    https://www.fmz.com/strategy/437553 (PineScript v4, FMZ last modified 2024-01-03 16:51:03).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 141-184), 123 length input 14 / CoG length input 20 (passed swapped), K smoothing 1, D 3, level 50; m 5, percent 1, signal line 1; reverse off
    Reversal123(LengthCoF = 20, ...);  CenterOfGravity(Length = 14, m = 5, Percent = 1, line 1): xLG = linreg(close, 14, 5), pos = 1 if close > xLG + close x 1 %, -1 if close < xLG - close x 1 %, else pos[1]
    agree -> entry, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script passes LengthCoF (20) to the 123 reversal and Length (14) to the centre of gravity: kept
      as written. linreg(src, n, offset) is the least-squares line's value offset bars back from the
      newest. The 123 test is read as written. The state is a level, so the entry is sent on every bar of
      the state; state 0 closes. REVERSAL INTENDED. No sizing code. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and a percent channel around a regression line.
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

NAME = "fmz_437553_reversal123_center_of_gravity"
FAMILY = "reversal_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_cof": [20, 14],
    "length": [14, 28],
}
DEFAULT_PARAMS = {"length_cof": 20, "length": 14, "k_smoothing": 1, "d_length": 3, "level": 50.0, "m": 5,
                  "percent": 1.0, "signal_line": 1, "reverse": False}


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


def _linreg(x, n, off):
    sx = n * (n - 1) / 2
    sxx = (n - 1) * n * (2 * n - 1) / 6
    sxy = sum((n - 1 - k) * x.shift(k) for k in range(n))
    sy = x.rolling(n).sum()
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    icpt = (sy - slope * sx) / n
    return icpt + slope * (n - 1 - off)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length_cof"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    vfast = st.rolling(int(p["k_smoothing"])).mean()
    vslow = vfast.rolling(int(p["d_length"])).mean()
    lvl = float(p["level"])
    c1, c2 = c.shift(1), c.shift(2)
    up_ = ((c2 < c1) & (c > c1) & (vfast < vslow) & (vfast > lvl)).to_numpy()
    dn_ = ((c2 > c1) & (c < c1) & (vfast > vslow) & (vfast < lvl)).to_numpy()
    xlg = _linreg(c, int(p["length"]), int(p["m"]))
    k = 1 if int(p["signal_line"]) == 1 else 2
    band = c * float(p["percent"]) / 100 * k
    r_, s_ = (c > xlg + band).to_numpy(), (c < xlg - band).to_numpy()
    m = len(c)
    sig = np.zeros(m)
    p123 = pg = 0.0
    for i in range(m):
        if up_[i]:
            p123 = 1.0
        elif dn_[i]:
            p123 = -1.0
        if r_[i]:
            pg = 1.0
        elif s_[i]:
            pg = -1.0
        sig[i] = 1.0 if (p123 == 1.0 and pg == 1.0) else (-1.0 if (p123 == -1.0 and pg == -1.0) else 0.0)
    if p["reverse"]:
        sig = -sig
    ix = bars_df.index
    flat = pd.Series(sig == 0, index=ix)
    return pd.Series(sig == 1, index=ix), flat, pd.Series(sig == -1, index=ix), flat.copy()


def portfolio_kwargs(**params):
    return {}
