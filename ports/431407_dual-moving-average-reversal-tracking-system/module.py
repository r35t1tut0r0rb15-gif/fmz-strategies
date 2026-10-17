"""HPotter combo, 1-hour bars: the 123 reversal and an Ichimoku state (short under the 52-bar Donchian mid 26 bars back,
long over the Tenkan / Kijun average 26 bars back) must agree; both long holds a long, both short holds a short, any
disagreement closes everything.
Port of FMZ strategy #431407 "Dual Moving Average Reversal Tracking System" (Combo Backtest 123 Reversal & Ichimoku2c).

FMZ source id: 431407

Source
    https://www.fmz.com/strategy/431407 (PineScript v4, FMZ last modified 2023-11-07 16:00:33).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 165-231), 123 reversal stoch 14 / 1 / 3, level 50; Ichimoku 9 / 26 / 52, displacement 26
    posReversal123: close[2] < close[1] < close and K < D and K > 50 -> 1; mirror -> -1; else hold
    SenkouA = donchian mid(52); SenkouB = (Tenkan[26] + Kijun[26]) / 2
    pos = close < SenkouA[26] ? -1 : close > SenkouB ? 1 : pos[1]
    both 1 -> entry long; both -1 -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The span names and the asymmetric displacement are as written. "Trade reverse" defaults to false
      and is fixed. strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a stochastic and Donchian midpoints.
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

NAME = "fmz_431407_combo_123_ichimoku2c"
FAMILY = "combo_123_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 28],
    "displacement": [26, 13],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "conv": 9, "base": 26, "span2": 52,
                  "displacement": 26}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _hold(cond_up, cond_dn):
    m = len(cond_up)
    out = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if cond_up[i]:
            q = 1
        elif cond_dn[i]:
            q = -1
        out[i] = q
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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["k_smoothing"])).mean()
    d = k.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    pos1 = _hold(((c2 < c1) & (c > c1) & (k < d) & (k > p["level"])).to_numpy(),
                 ((c2 > c1) & (c < c1) & (k > d) & (k < p["level"])).to_numpy())

    def mid(L):
        return (h.rolling(L).max() + lo.rolling(L).min()) / 2
    base = int(p["base"])
    span_a = mid(int(p["span2"]))
    span_b = (mid(int(p["conv"])).shift(base) + mid(base).shift(base)) / 2
    dn = (c < span_a.shift(int(p["displacement"]))).to_numpy()
    pos2 = _hold((c > span_b).to_numpy() & ~dn, dn)
    tgt = np.where((pos1 == 1) & (pos2 == 1), 1, np.where((pos1 == -1) & (pos2 == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
