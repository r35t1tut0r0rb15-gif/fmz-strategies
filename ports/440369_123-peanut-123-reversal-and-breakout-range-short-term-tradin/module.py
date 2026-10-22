"""123 reversal and breakout-range-short combo, 1-hour bars, short only: short when the 123 state is down and the low breaks under the previous 4-bar low; flat otherwise (the breakout side is never up,
so no long can occur).
Port of FMZ strategy #440369 "坚果123反转与突破范围短线交易策略Peanut-123-Reversal-and-Breakout-Range-Short-term-Trading-Strategy" (Combo Backtest 123 Reversal & Breakout Range Short).

FMZ source id: 440369

Source
    https://www.fmz.com/strategy/440369 (PineScript v4, FMZ last modified 2024-01-29 16:31:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 174-207), 123: 14 / 1 / 3 / 50; look-back 4; reverse off
    123 pos (close pattern and stochastic);  BRS pos = low < lowest(low, 4)[1] ? -1 : 0;  both 1 -> entry Long, both -1 -> entry Short, otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The breakout-range part only returns -1 or 0, so the combined state is short or flat. The 123
      test is read as written. Short only: Opposite entries cannot occur. No sizing code. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close pattern, stochastic and a range breakout.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #428626, Jaccard 0.715); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only: Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440369_reversal123_breakout_range_short"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "look_bak": [4, 10],
}
DEFAULT_PARAMS = {"length": 14, "look_bak": 4, "k_smoothing": 1, "d_length": 3, "level": 50.0}


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
    brk = (lo < lo.rolling(int(p["look_bak"])).min().shift(1)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    p123 = 0
    for i in range(m):
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        tgt[i] = -1 if (p123 == -1 and brk[i]) else 0
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return false, false.copy(), pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix)


def portfolio_kwargs(**params):
    return {}
