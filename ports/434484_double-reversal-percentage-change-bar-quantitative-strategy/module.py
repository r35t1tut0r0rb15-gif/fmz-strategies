"""HPotter combo of the 123 reversal and a percent-change bar, 1-hour bars: long while both say up, short while both say
down, flat otherwise. The percent side is up after a bar closing more than 0.33 % above the previous close and down after
one closing more than 0.33 % below it.
Port of FMZ strategy #434484 "Double Reversal Percentage Change Bar Quantitative Strategy" (Combo Backtest 123 Percent change bar).

FMZ source id: 434484

Source
    https://www.fmz.com/strategy/434484 (PineScript v4, FMZ last modified 2023-12-06 17:44:35).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 209-250), stoch 14 / 1 / 3, level 50; percent change (not price), look back 1, zones -0.33 / 0.33; reverse false
    p123 as Reversal123(14, 1, 3, 50);  chg = (close - close[1]) x 100 / close[1];  pcb = chg > 0.33 ? 1 : chg < -0.33 ? -1 : pcb[1]
    both 1 -> entry long;  both -1 -> entry short;  otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each side keeps its last state until it changes. strategy.entry reverses: REVERSAL INTENDED.
      The percent (not price) change is the default. reverse is false. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and percent changes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #435701, Jaccard 0.650); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434484_combo_123_percent_change"
FAMILY = "combo_123_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "zone": [0.33, 0.66],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "barsback": 1, "zone": 0.33}


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
    cb = c.shift(int(p["barsback"]))
    chg = (c - cb) * 100 / cb
    z = float(p["zone"])
    pcb = _hold((chg > z).to_numpy(), (chg < -z).to_numpy())
    tgt = np.where((p123 == 1) & (pcb == 1), 1, np.where((p123 == -1) & (pcb == -1), -1, 0)).astype(np.int8)
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
