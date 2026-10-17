"""HPotter combo of the 123 reversal and Bill Williams' accelerator oscillator, 2-hour bars: long while both sides say up,
short while both say down, flat otherwise. The AC side is up when (SMA 5 - SMA 34 of hl2) minus its SMA 5 is above zero,
down below zero.
Port of FMZ strategy #433911 "Reverse Triad Quantitative Strategy" (Combo Backtest 123 Reversal and Accelerator Oscillator (AC)).

FMZ source id: 433911

Source
    https://www.fmz.com/strategy/433911 (PineScript v3, FMZ last modified 2023-12-01 14:14:46).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 151-190), stoch 14 / 1 / 3, level 50; AC slow 34, fast 5; reverse false
    p123 as Reversal123(14, 1, 3, 50);  ao = sma(hl2, 5) - sma(hl2, 34);  ac = ao - sma(ao, 5);  pac = ac > 0 ? 1 : ac < 0 ? -1 : pac[1]
    both 1 -> entry long;  both -1 -> entry short;  otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each side keeps its last state until it changes. strategy.entry reverses: REVERSAL INTENDED.
      reverse is false. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and an average-difference sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430763 (3 members, best partner #430763, Jaccard 0.693); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433911_combo_123_accelerator"
FAMILY = "combo_123_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "slow": [34, 55],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "slow": 34, "fast": 5}


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
    p123 = _hold(((c2 < c1) & (c > c1) & (k < d) & (k > p["level"])).to_numpy(),
                 ((c2 > c1) & (c < c1) & (k > d) & (k < p["level"])).to_numpy())
    hl2 = (h + lo) / 2
    f = int(p["fast"])
    ao = hl2.rolling(f).mean() - hl2.rolling(int(p["slow"])).mean()
    ac = ao - ao.rolling(f).mean()
    pac = _hold((ac > 0).to_numpy(), (ac < 0).to_numpy())
    tgt = np.where((p123 == 1) & (pac == 1), 1, np.where((p123 == -1) & (pac == -1), -1, 0)).astype(np.int8)
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
