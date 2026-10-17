"""HPotter combo of the 123 reversal and Bill Williams' three displaced averages, 1-hour bars: long while both sides say up,
short while both say down, flat otherwise. The averages side is down when the close is under the SMA 5 [3] < SMA 8 [5]
< SMA 13 [8] stack of hl2 and up for the mirror, otherwise it keeps its state.
Port of FMZ strategy #433540 "Combo Trend Reversal Moving Average Crossover Strategy" (Combo Backtest 123 Reversal & Bill Williams Averages. 3Lines).

FMZ source id: 433540

Source
    https://www.fmz.com/strategy/433540 (PineScript v3, FMZ last modified 2023-11-28 13:47:05).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 158-199), stoch 14 / 1 / 3, level 50; SMA hl2 13 / 8 / 5 with offsets 8 / 5 / 3; reverse false
    p123 as Reversal123(14, 1, 3, 50);  L = sma(hl2, 13)[8], M = sma(hl2, 8)[5], S = sma(hl2, 5)[3]
    pbw = close < S < M < L ? -1 : close > S > M > L ? 1 : pbw[1];  both 1 -> long;  both -1 -> short;  else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The offsets read the averages that many bars back (no future value). strategy.entry reverses:
      REVERSAL INTENDED. reverse is false. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and average order.
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

NAME = "fmz_433540_combo_123_williams_lines"
FAMILY = "combo_123_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "l_len": [13, 21],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "l_len": 13, "m_len": 8, "s_len": 5,
                  "l_off": 8, "m_off": 5, "s_off": 3}


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
    lm = hl2.rolling(int(p["l_len"])).mean().shift(int(p["l_off"]))
    mm = hl2.rolling(int(p["m_len"])).mean().shift(int(p["m_off"]))
    sm = hl2.rolling(int(p["s_len"])).mean().shift(int(p["s_off"]))
    pbw = _hold(((c > sm) & (sm > mm) & (mm > lm)).to_numpy(), ((c < sm) & (sm < mm) & (mm < lm)).to_numpy())
    tgt = np.where((p123 == 1) & (pbw == 1), 1, np.where((p123 == -1) & (pbw == -1), -1, 0)).astype(np.int8)
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
