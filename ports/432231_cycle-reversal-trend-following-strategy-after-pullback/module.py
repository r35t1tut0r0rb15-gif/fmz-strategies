"""HPotter combo of the 123 reversal and a detrended price oscillator, 1-hour bars: long while both sides say up, short
while both say down, flat otherwise. The 123 side turns up after two closes down then up with the stochastic K (14)
under its D (3) and above 50 (mirror for down); the DPO side is the sign of the close minus its SMA 14.
Port of FMZ strategy #432231 "Cycle Reversal Trend Following Strategy after Pullback" (Combo Backtest 123 Detrended Price Oscillator).

FMZ source id: 432231

Source
    https://www.fmz.com/strategy/432231 (PineScript v4, FMZ last modified 2023-11-15 17:13:18).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 205-241), stoch 14 / 1 / 3, level 50, DPO 14, reverse false
    p123 = close[2] < close[1] and close > close[1] and k < d and k > 50 ? 1 : close[2] > close[1] and close < close[1] and k > d and k < 50 ? -1 : p123[1]
    pdpo = close - sma(close, 14) > 0 ? 1 : < 0 ? -1 : pdpo[1]
    both 1 -> entry long;  both -1 -> entry short;  otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each side keeps its last state until it changes, as written; the combined state is acted on at
      every bar (flat when the sides disagree). strategy.entry reverses: REVERSAL INTENDED.
      reverse is false. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and SMA sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #437515, Jaccard 0.737); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432231_combo_123_dpo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "dpo_len": [14, 28],
}
DEFAULT_PARAMS = {"length": 14, "k_smooth": 1, "d_len": 3, "level": 50, "dpo_len": 14}


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
    res = (c - c.rolling(int(p["dpo_len"])).mean()).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    s1 = s2 = 0
    for i in range(m):
        if a_up[i]:
            s1 = 1
        elif a_dn[i]:
            s1 = -1
        if res[i] > 0:
            s2 = 1
        elif res[i] < 0:
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
