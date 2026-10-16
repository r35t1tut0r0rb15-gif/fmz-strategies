"""HPotter combo, 45-minute bars, long only as written: the 123 reversal says long and the high breaks
the previous 4-bar high -> long; any other bar closes it (the breakout leg never says short).
Port of FMZ strategy #428626 "Reversal Breakout Trend Strategy" (Combo 123 Reversal & Breakout Range Long).

FMZ source id: 428626

Source
    https://www.fmz.com/strategy/428626 (PineScript v3, FMZ last modified 2023-10-07 16:15:43).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 177-210), stoch 14 / K 1 / D 3 / level 50, look-back 4
    123: close[2] < close[1] and close > close[1] and K < D and K > 50 -> 1; mirror -> -1; else hold
    breakout = high > highest(high, 4)[1] ? 1 : 0 (never -1)
    both 1 -> entry long; both -1 (impossible) -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The breakout leg is 1 or 0, so the short combination can never occur: Long only, and every bar
      that is not a joint long signal closes the long, as written.
    * "Trade reverse" (default false) fixed off.
    * FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and channel lengths.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #440369, Jaccard 0.715); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428626_combo_123_reversal_breakout_long"
FAMILY = "combo_123_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21],
    "look_bak": [4, 10],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "look_bak": 4}


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
    a = _hold(r_up, r_dn)
    brk = (h > h.rolling(int(p["look_bak"])).max().shift(1)).to_numpy()
    tgt = np.where((a == 1) & brk, 1, 0).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
