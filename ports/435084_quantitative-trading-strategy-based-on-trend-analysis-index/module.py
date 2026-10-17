"""HPotter Trend Analysis Index, bar size pending: the 5-bar range of the SMA 28 as a percent of the close above 0.11 goes
long, below 0.02 goes short; held in between and reversed on the opposite level.
Port of FMZ strategy #435084 "Quantitative Trading Strategy Based on Trend Analysis Index" (Trend Analysis Index).

FMZ source id: 435084

Source
    https://www.fmz.com/strategy/435084 (PineScript v2, FMZ last modified 2023-12-12 10:40:52).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 142-162), SMA 28, TAI 5, top 0.11, low 0.02; reverse false; no backtest header
    tai = (highest(sma28, 5) - lowest(sma28, 5)) x 100 / close;  pos = tai > 0.11 ? 1 : tai < 0.02 ? -1 : pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1).
      precompute builds the bars with the house bar_sizes.build_bars(raw_1m_df, params["bar_size"]);
      the driver supplies bar_size (never in GRID / DEFAULT_PARAMS).
    * strategy.entry reverses: REVERSAL INTENDED. reverse is false.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a percent slope range.
    3 crypto-exchange-only: no.
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

NAME = "fmz_435084_trend_analysis_index"
FAMILY = "slope_momentum"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size: the driver supplies params["bar_size"]
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "avg_len": [28, 14],
    "top": [0.11, 0.3],
}
DEFAULT_PARAMS = {"avg_len": 28, "tai_len": 5, "top": 0.11, "low": 0.02}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    s = c.rolling(int(p["avg_len"])).mean()
    k = int(p["tai_len"])
    tai = (s.rolling(k).max() - s.rolling(k).min()) * 100 / c
    up, dn = (tai > float(p["top"])).to_numpy(), (tai < float(p["low"])).to_numpy()
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
