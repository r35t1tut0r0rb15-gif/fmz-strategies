"""123 reversal and stochastic crossover combination, 10-minute bars: the 123 reversal state and the stochastic state (fast 7 under its D 3 with both over 70: long; fast at or above D with both under 20:
short) agreeing long go long, agreeing short go short, disagreeing close all; reversing.
Port of FMZ strategy #439087 "Price Reversal with Crossover Capturing Strategy" (Combo).

FMZ source id: 439087

Source
    https://www.fmz.com/strategy/439087 (PineScript v4, FMZ last modified 2024-01-17 16:29:13).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 164-205), 123: length 14, K smoothing 1, D 3, level 50; stochastic 7 / 3, oversold 20, overbought 70; reverse off
    StochCross: k = stoch(close, high, low, 7), d = sma(k, 3);  pos = 1 if k < d and k > 70 and d > 70, -1 if k >= d and k < 20 and d < 20, else pos[1]
    Reversal123 as in the combo family;  agree -> entry, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 123 test and the stochastic states are read as written (long when the fast line is under D in
      overbought territory). The states are levels; disagreement closes. REVERSAL INTENDED. No sizing
      code. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns and stochastic states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #436215, Jaccard 0.712); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439087_reversal123_stoch_cross_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "length_sc": [7, 14],
}
DEFAULT_PARAMS = {"length": 14, "length_sc": 7, "k_smoothing": 1, "d_length": 3, "level": 50.0,
                  "d_length_sc": 3, "oversold": 20.0, "overbought": 70.0, "reverse": False}


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


def _stoch(h, lo, c, n):
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        return 100.0 * (c - ll) / (hh - ll).where(hh > ll)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    vfast = _stoch(h, lo, c, int(p["length"])).rolling(int(p["k_smoothing"])).mean()
    vslow = vfast.rolling(int(p["d_length"])).mean()
    lvl = float(p["level"])
    c1, c2 = c.shift(1), c.shift(2)
    up_ = ((c2 < c1) & (c > c1) & (vfast < vslow) & (vfast > lvl)).to_numpy()
    dn_ = ((c2 > c1) & (c < c1) & (vfast > vslow) & (vfast < lvl)).to_numpy()
    k = _stoch(h, lo, c, int(p["length_sc"]))
    d = k.rolling(int(p["d_length_sc"])).mean()
    ob, os_ = float(p["overbought"]), float(p["oversold"])
    sc_up = ((k < d) & (k > ob) & (d > ob)).to_numpy()
    sc_dn = ((k >= d) & (k < os_) & (d < os_)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    p123 = psc = 0
    for i in range(m):
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        if sc_up[i]:
            psc = 1
        elif sc_dn[i]:
            psc = -1
        tgt[i] = 1 if (p123 == 1 and psc == 1) else (-1 if (p123 == -1 and psc == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
