"""HPotter combo, no bar size in the source: the 123 reversal and a range state (the 13-bar SMA of bar ranges, 4 bars back,
above the current range long, below it short) must agree; both long holds a long, both short holds a short, any
disagreement closes everything.
Port of FMZ strategy #430545 "Momentum Reversal Multi Timeframe Strategy" (Combo Backtest 123 Reversal & (H-L)/C Histogram).

FMZ source id: 430545

Source
    https://www.fmz.com/strategy/430545 (PineScript v3, FMZ last modified 2023-10-30 10:42:54).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 201-264), stochastic 14 / 1 / 3, level 50; range SMA 13, look-back 4, "% change" off (price range)
    123: close[2] < close[1] and close > close[1] and K < D and K > 50 -> 1; mirror -> -1; else pos[1]
    r = high - low; s = sma(|r|, 13); s[4] > |r| -> 1; s[4] < |r| -> -1; else pos[1]
    both 1 -> entry long; both -1 -> entry short; otherwise strategy.close_all()

Interpretation choices (Pine rules in SURVEY_README.md)
    * The range is compared with its own average, so the price-unit range is scale-free (criterion 2
      holds as written).
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1).
      precompute builds the bars with the house bar_sizes.build_bars(raw_1m_df, params["bar_size"]);
      the driver supplies bar_size (never in GRID / DEFAULT_PARAMS).
    * "Trade reverse" defaults to false and is fixed. A one-bar change from long to short reverses:
      REVERSAL INTENDED.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels and a range against its own average.
    3 crypto-exchange-only: no (no exchange or market named).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_430545_combo_123_range_hist"
FAMILY = "combo_123_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "bar_size_pending"
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_length": [13, 26],
    "bars_back": [4, 1],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "sma_length": 13, "bars_back": 4}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["k_smoothing"])).mean()
    d = k.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    pos1 = _hold(((c2 < c1) & (c > c1) & (k < d) & (k > p["level"])).to_numpy(),
                 ((c2 > c1) & (c < c1) & (k > d) & (k < p["level"])).to_numpy())
    r = (h - lo).abs()
    s = r.rolling(int(p["sma_length"])).mean().shift(int(p["bars_back"]))
    pos2 = _hold((s > r).to_numpy(), (s < r).to_numpy())
    tgt = np.where((pos1 == 1) & (pos2 == 1), 1, np.where((pos1 == -1) & (pos2 == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
