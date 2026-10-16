"""HPotter combo, 5-minute bars: the 123 reversal and the close against the 14-bar linear-regression
intercept must agree; long when both say long, short when both say short, flat otherwise.
Port of FMZ strategy #427884 "Reversal and Linear Regression Intercept Combo Strategy".

FMZ source id: 427884

Source
    https://www.fmz.com/strategy/427884 (PineScript v4, FMZ last modified 2023-09-26 15:56:48).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 287-330), stoch 14 / K 1 / D 3 / level 50, LRI 14 of close
    123: close[2] < close[1] and close > close[1] and K < D and K > 50 -> 1; mirror -> -1; else hold
    LRI: X = L (L - 1) / 2; slope = (L sum(i x[i]) - X sum(x)) / (X^2 - L^2 (L - 1)(2L - 1) / 6);
         LRI = (sum(x) - slope X) / L; close > LRI -> 1; close < LRI -> -1; else hold
    both 1 -> entry long; both -1 -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The LRI formula is ported as written (i counts bars back, so its "slope" has the opposite sign
      of the usual one; the intercept is the value at the current bar).
    * "Trade reverse" (default false) is fixed off. strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and regression lengths only.
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

NAME = "fmz_427884_combo_123_reversal_lri"
FAMILY = "combo_123_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21],
    "length_lri": [14, 28],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "length_lri": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _hold(up, dn):
    out = np.zeros(len(up), dtype=np.int8)
    pos = 0
    for i in range(len(up)):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        out[i] = pos
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _lri(x, L):
    xx = L * (L - 1) * 0.5
    div = xx * xx - L * L * (L - 1) * (2 * L - 1) / 6
    w = np.arange(L, dtype=float)                       # i = 0 (current bar) .. L - 1
    xxy = x.rolling(L).apply(lambda v: np.dot(v[::-1], w), raw=True)
    s = x.rolling(L).sum()
    slope = (L * xxy - xx * s) / div
    return (s - slope * xx) / L


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["k_smoothing"])).mean()
    d = k.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    lv = p["level"]
    r_up = ((c2 < c1) & (c > c1) & (k < d) & (k > lv)).to_numpy()
    r_dn = ((c2 > c1) & (c < c1) & (k > d) & (k < lv)).to_numpy()
    lri = _lri(c, int(p["length_lri"]))
    a, b = _hold(r_up, r_dn), _hold((c > lri).to_numpy(), (c < lri).to_numpy())
    tgt = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
