"""HPotter combo of the 123 reversal and the ergodic TSI, 1-hour bars: long while both sides say up, short while both say
down, flat otherwise. The 123 side is as in the other combo ports (stochastic 14 / 1 / 3, level 50); the TSI side is up
while the triple-smoothed TSI (4 / 8 / 6) is above its EMA 3 and down while below.
Port of FMZ strategy #432757 "Multi factor Momentum Reversal Combo Strategy" (Combo Backtest 123 Reversal & Ergodic TSI).

FMZ source id: 432757

Source
    https://www.fmz.com/strategy/432757 (PineScript v4, FMZ last modified 2023-11-21 11:20:31).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 228-274), stoch 14 / 1 / 3, level 50, TSI 4 / 8 / 6, signal 3, reverse false
    tsi = 100 x ema(ema(ema(change, 4), 8), 6) / ema(ema(ema(|change|, 4), 8), 6) (0 when the denominator is 0)
    ptsi = tsi > ema(tsi, 3) ? 1 : tsi < ema(tsi, 3) ? -1 : ptsi[1]
    both 1 -> entry long;  both -1 -> entry short;  otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each side keeps its last state until it changes, as written. strategy.entry reverses: REVERSAL
      INTENDED. reverse is false. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and TSI states.
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

NAME = "fmz_432757_combo_123_ergodic_tsi"
FAMILY = "combo_123_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "smth": [3, 6],
}
DEFAULT_PARAMS = {"length": 14, "k_smooth": 1, "d_len": 3, "level": 50, "r": 4, "s": 8, "u": 6, "smth": 3}


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
    e3 = lambda x: (x.ewm(span=int(p["r"]), adjust=False).mean().ewm(span=int(p["s"]), adjust=False).mean()  # noqa: E731
                    .ewm(span=int(p["u"]), adjust=False).mean())
    ch = c.diff()
    num, den = 100 * e3(ch), e3(ch.abs())
    tsi = (num / den).where(den != 0, 0.0)
    sig = tsi.ewm(span=int(p["smth"]), adjust=False).mean()
    t_up, t_dn = (tsi > sig).to_numpy(), (tsi < sig).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    s1 = s2 = 0
    for i in range(m):
        if a_up[i]:
            s1 = 1
        elif a_dn[i]:
            s1 = -1
        if t_up[i]:
            s2 = 1
        elif t_dn[i]:
            s2 = -1
        tgt[i] = 1 if (s1 == 1 and s2 == 1) else (-1 if (s1 == -1 and s2 == -1) else 0)
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
