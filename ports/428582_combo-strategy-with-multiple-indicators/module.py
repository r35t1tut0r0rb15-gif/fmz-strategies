"""HPotter combo, 45-minute bars: the 123 reversal and the close against TEMA 26 must agree; long when
both say long, short when both say short, flat otherwise.
Port of FMZ strategy #428582 "Combo Strategy with Multiple Indicators" (Combo 123 Reversal & TEMA1).

FMZ source id: 428582

Source
    https://www.fmz.com/strategy/428582 (PineScript v4, FMZ last modified 2023-10-07 10:25:40).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 138-179), stoch 14 / K 1 / D 3 / level 50, TEMA 26
    123: close[2] < close[1] and close > close[1] and K < D and K > 50 -> 1; mirror -> -1; else hold
    TEMA = 3 ema1 - 3 ema2 + ema3; close > TEMA -> 1; close < TEMA -> -1; else hold
    both 1 -> entry long; both -1 -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Trade reverse" (default false) fixed off. strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and MA lengths.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #440094, Jaccard 0.657); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428582_combo_123_reversal_tema"
FAMILY = "combo_123_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21],
    "length_tema": [26, 50],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "length_tema": 26}


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
    t = int(p["length_tema"])
    e1 = c.ewm(span=t, adjust=False).mean()
    e2 = e1.ewm(span=t, adjust=False).mean()
    e3 = e2.ewm(span=t, adjust=False).mean()
    tema = 3 * e1 - 3 * e2 + e3
    a, b = _hold(r_up, r_dn), _hold((c > tema).to_numpy(), (c < tema).to_numpy())
    tgt = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
