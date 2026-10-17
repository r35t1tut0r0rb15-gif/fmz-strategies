"""HPotter combo of the 123 reversal and the key reversal down, 3-hour bars: short while the 123 side says down and the bar
is a key reversal down (a new high above the previous bar's high with a lower close), flat otherwise; the key-reversal
side is never long, so the combo never goes long.
Port of FMZ strategy #432921 "Dual Reversal Tracking Strategy" (Combo Backtest 123 Reversal & Key Reversal Down).

FMZ source id: 432921

Source
    https://www.fmz.com/strategy/432921 (PineScript v4, FMZ last modified 2023-11-22 17:42:23).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 166-200), stoch 14 / 1 / 3, level 50, key reversal 1 bar, reverse false
    krd = high > highest(high[1], 1) and close < close[1] ? -1 : 0;  p123 as Reversal123(14, 1, 3, 50)
    both 1 -> entry long (never: krd is not 1);  both -1 -> entry short;  otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The key-reversal side is -1 or 0 on each bar (it keeps no state), so a short lasts only while
      key-reversal bars follow each other; any other bar closes it. Short only in effect; Opposite
      entries cannot occur. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and a bar pattern.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #435288, Jaccard 0.765); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only in effect (the long branch cannot fire). Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432921_combo_123_key_reversal_down"
FAMILY = "combo_123_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "n_len": [1, 3],
}
DEFAULT_PARAMS = {"length": 14, "k_smooth": 1, "d_len": 3, "level": 50, "n_len": 1}


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
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["k_smooth"])).mean()
    d = k.rolling(int(p["d_len"])).mean()
    lv = float(p["level"])
    c1, c2 = c.shift(1), c.shift(2)
    a_up = ((c2 < c1) & (c > c1) & (k < d) & (k > lv)).to_numpy()
    a_dn = ((c2 > c1) & (c < c1) & (k > d) & (k < lv)).to_numpy()
    krd = ((h > h.shift(1).rolling(int(p["n_len"])).max()) & (c < c1)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    s1 = 0
    for i in range(m):
        if a_up[i]:
            s1 = 1
        elif a_dn[i]:
            s1 = -1
        tgt[i] = -1 if (s1 == -1 and krd[i]) else 0
    prev = np.concatenate(([0], tgt[:-1]))
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (false, false.copy(), se, sx))


def portfolio_kwargs(**params):
    return {}
